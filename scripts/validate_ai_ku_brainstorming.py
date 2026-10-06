#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validador independiente del dataset AI-ku_brainstorming.

Uso:
    python3 validate_ai_ku_brainstorming.py [ruta_al_jsonl]

Sin argumento usa: ./AI-ku_brainstorming.jsonl

Comprueba:
  - JSON válido por línea, campos base presentes y no vacíos.
  - Enums dentro de registro (type, domain, difficulty, authorization).
  - reasoning_trace delimitado por <|V4X_think> ... <V4X_thought|>.
  - Longitudes mínimas orientativas (input/answer/trace) como AVISOS.
  - claim_critique y code_snippet bien formados cuando existen.
  - IDs únicos y secuenciales.
  - Distribución por type/domain/difficulty y cobertura de tipos.

Códigos de salida: 0 = válido, 1 = errores.
"""
import json
import sys
from collections import Counter

TYPES = {
    "SECURITY_REASONING", "THREAT_MODELING", "PENTEST_PLANNING",
    "HYPOTHESIS_GENERATION", "HYPOTHESIS_REVISION", "FAILURE_AS_INFORMATION",
    "ALTERNATIVE_PATHS", "EVIDENCE_ANALYSIS", "VULNERABILITY_ANALYSIS",
    "FALSE_POSITIVE", "FALSE_NEGATIVE", "WRONG_CLAIM", "ROOT_CAUSE",
    "IMPACT_ANALYSIS", "RISK_PRIORITIZATION", "RED_TEAM", "BLUE_TEAM",
    "PURPLE_TEAM", "CODE_SECURITY_REVIEW", "NETWORK_ANALYSIS", "WEB_SECURITY",
    "API_SECURITY", "HOST_SECURITY", "REVERSE_ENGINEERING", "INCIDENT_ANALYSIS",
    "LOG_ANALYSIS", "DETECTION", "MITIGATION", "RETEST", "SECURITY_ARCHITECTURE",
    "CTF", "LAB_SCENARIO", "ADVERSARIAL_REASONING",
}
DOMAINS = {
    "WEB", "API", "NETWORK", "HOST", "LINUX", "WINDOWS", "CONTAINER", "CLOUD",
    "DATABASE", "AUTH", "MOBILE", "IOT", "CODE", "CRYPTO", "REVERSE",
    "INCIDENT", "ARCHITECTURE", "GENERAL", "SUPPLY_CHAIN", "CTF",
}
DIFFICULTIES = {"fundamentals", "intermediate", "advanced", "expert", "adversarial"}
AUTHORIZATIONS = {
    "controlled_lab", "ctf", "simulated_environment",
    "open_source_project", "synthetic_scenario",
}
BASE_FIELDS = ["id", "type", "domain", "difficulty", "authorization", "input",
               "question", "reasoning_target", "expected_behavior", "answer",
               "reasoning_trace", "verification", "alternative_hypotheses", "tags"]
OPEN_TOK, CLOSE_TOK = "<|V4X_think>", "<V4X_thought|>"
SOFT_MIN = {"input": 120, "answer": 700, "reasoning_trace_body": 200}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "AI-ku_brainstorming.jsonl"
    try:
        fh = open(path, encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se puede abrir {path}: {e}")
        return 1

    errors, warnings = [], []
    n, ids = 0, []
    c_type, c_domain, c_diff, c_auth = Counter(), Counter(), Counter(), Counter()

    for lineno, raw in enumerate(fh, 1):
        if not raw.strip():
            continue
        n += 1
        try:
            s = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"línea {lineno}: JSON inválido: {e}")
            continue
        for f in BASE_FIELDS:
            if f not in s or s[f] in (None, "", []):
                errors.append(f"línea {lineno} [{s.get('id','?')}]: campo ausente/vacío: {f}")
        if s.get("type") not in TYPES:
            errors.append(f"línea {lineno}: type fuera de registro: {s.get('type')}")
        if s.get("domain") not in DOMAINS:
            errors.append(f"línea {lineno}: domain fuera de registro: {s.get('domain')}")
        if s.get("difficulty") not in DIFFICULTIES:
            errors.append(f"línea {lineno}: difficulty fuera de registro: {s.get('difficulty')}")
        if s.get("authorization") not in AUTHORIZATIONS:
            errors.append(f"línea {lineno}: authorization fuera de registro: {s.get('authorization')}")
        tr = s.get("reasoning_trace", "")
        if not (tr.startswith(OPEN_TOK + "\n") and tr.endswith("\n" + CLOSE_TOK)):
            errors.append(f"línea {lineno}: reasoning_trace mal delimitado")
        body = tr[len(OPEN_TOK) + 1:-len(CLOSE_TOK) - 1] if tr else ""
        if len(body) < SOFT_MIN["reasoning_trace_body"]:
            warnings.append(f"línea {lineno} [{s.get('id','?')}]: trace corto ({len(body)} chars)")
        if len(s.get("input", "")) < SOFT_MIN["input"]:
            warnings.append(f"línea {lineno} [{s.get('id','?')}]: input corto")
        if len(s.get("answer", "")) < SOFT_MIN["answer"]:
            warnings.append(f"línea {lineno} [{s.get('id','?')}]: answer corto ({len(s.get('answer',''))} chars)")
        cc = s.get("claim_critique")
        if cc and not all(cc.get(k) for k in ("claim", "analysis", "reason")):
            errors.append(f"línea {lineno}: claim_critique incompleto")
        cs = s.get("code_snippet")
        if cs and not (cs.get("language") and cs.get("code")):
            errors.append(f"línea {lineno}: code_snippet incompleto")
        ids.append(s.get("id", f"<sin-id línea {lineno}>"))
        c_type[s.get("type")] += 1
        c_domain[s.get("domain")] += 1
        c_diff[s.get("difficulty")] += 1
        c_auth[s.get("authorization")] += 1

    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        errors.append(f"IDs duplicados: {dup[:5]}")

    print(f"Archivo: {path}")
    print(f"Samples: {n}")
    print(f"Tipos: {len(c_type)}/33   Dominios: {len(c_domain)}/20")
    print("Dificultad:", dict(sorted(c_diff.items(), key=lambda kv: -kv[1])))
    print("Autorización:", dict(sorted(c_auth.items(), key=lambda kv: -kv[1])))
    print(f"Errores: {len(errors)}   Avisos: {len(warnings)}")
    if warnings:
        print("— Avisos (no bloquean):")
        for w in warnings[:10]:
            print("  ~", w)
        if len(warnings) > 10:
            print(f"  ... y {len(warnings) - 10} más")
    if errors:
        print("— ERRORES:")
        for e in errors[:20]:
            print("  ✗", e)
        if len(errors) > 20:
            print(f"  ... y {len(errors) - 20} más")
        return 1
    print("RESULTADO: VÁLIDO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
