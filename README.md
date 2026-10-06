# AI-ku_brainstorming

**Dataset de razonamiento de pentester / ethical hacker / security researcher para el Expert 177 de AI-ku.**

Dataset de entrenamiento en formato JSONL con **220 samples** de razonamiento de
seguridad, todos situados en entornos **autorizados** (laboratorios, CTF,
simulaciones, proyectos open source). Filosofía central:

```
observar → formular hipótesis → probar → interpretar → actualizar → verificar → concluir
```

El objetivo NO es memorizar vulnerabilidades ni comandos. Es aprender a **pensar**:
generar hipótesis, distinguir evidencia, aprender del fallo (*fail forward*),
cambiar de superficie con justificación, priorizar por valor informativo, demostrar
impacto y localizar la causa raíz.

---

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `data/AI-ku_brainstorming.jsonl` | El dataset: 220 samples, un JSON por línea (UTF-8) |
| `stats/AI-ku_brainstorming_stats.json` | Estadísticas por type / domain / difficulty / authorization |
| `scripts/validate_ai_ku_brainstorming.py` | Validador independiente re-ejecutable |
| `README.md` | Este documento |

---

## Campos base (todos los samples)

| Campo | Tipo | Contenido |
|---|---|---|
| `id` | string | `br_000001` … secuencial determinista |
| `type` | enum EN | Uno de los 33 tipos (ver tabla siguiente) |
| `domain` | enum EN | `WEB, API, NETWORK, HOST, LINUX, WINDOWS, CONTAINER, CLOUD, AUTH, CODE, CRYPTO, REVERSE, INCIDENT, ARCHITECTURE, IOT, MOBILE, SUPPLY_CHAIN, CTF, GENERAL` |
| `difficulty` | enum EN | `fundamentals, intermediate, advanced, expert, adversarial` (el nivel `adversarial` corresponde al *adversarial-ambiguous* de la especificación §26) |
| `authorization` | enum EN | `controlled_lab, ctf, simulated_environment, open_source_project, synthetic_scenario` |
| `input` | string ES | El escenario: descripción del laboratorio/CTF/simulación y lo observado |
| `question` | string ES | La pregunta que el Expert 177 debe responder |
| `reasoning_target` | lista EN | Habilidades que el sample entrena (`identify_attack_surface`, `generate_hypotheses`, `revise_hypothesis`, `distinguish_evidence_levels`, …) |
| `expected_behavior` | string ES | Qué debe caracterizar una buena respuesta |
| `answer` | string ES | El razonamiento completo y auditable (≈300–600 palabras): hipótesis, evidencia, decisiones, justificaciones |
| `reasoning_trace` | string ES | Bloque delimitado con el razonamiento ESTRUCTURADO y OBSERVABLE (no cadena de pensamiento privada): hipótesis → evidencia (OBSERVED/INFERRED/UNKNOWN) → decisión → siguiente prueba → si falla |
| `verification` | string ES | Cómo se verifica/reproduce la conclusión |
| `alternative_hypotheses` | lista ES | Hipótesis alternativas vivas o explicaciones rivales |
| `tags` | lista EN | Etiquetas temáticas |

### Campos opcionales (flexible por tipo, §25)

| Campo | Aparece en | Contenido |
|---|---|---|
| `remediation` | VULN/ROOT/MITIGATION/PURPLE/… | Corrección que elimina la CAUSA, no el síntoma |
| `claim_critique` | FALSE_POSITIVE / WRONG_CLAIM | `{claim, analysis, reason}`: afirmación errónea + refutación estructurada (§27) |
| `code_snippet` | CODE_SECURITY_REVIEW y otros | `{language, code}`: fragmento didáctico de laboratorio |
| `detection_ideas` | DETECTION / BLUE / PURPLE | Reglas de detección propuestas |
| `log_source` | LOG/INCIDENT/DETECTION/BLUE | Fuentes de registro implicadas |
| `retest_plan` | RETEST / PURPLE / ROOT | Plan de re-verificación de la corrección |
| `strategy_shift` | HYPOTHESIS_REVISION | La transición de estrategia justificada |
| `mitre_reference` | RED/BLUE/PURPLE/DETECTION | Tácticas MITRE ATT&CK como referencia conceptual |
| `prioritization_rationale` | RISK_PRIORITIZATION | Criterio explícito de la priorización |
| `reflection_questions` | varios | Preguntas de meta-cognición operativa (§28) |

---

## Delimitadores del bloque de razonamiento

Apertura y cierre **exactos**, una sola vez cada uno, siempre dentro del campo
`reasoning_trace` de cada sample:

```
<|V4X_think>
... razonamiento observable en español ...
<V4X_thought|>
```

- **Apertura:** `<|V4X_think>` — pipe ANTES de `V4X`.
- **Cierre:** `<V4X_thought|>` — pipe DESPUÉS de `thought`, antes del `>`.
- Verificado programáticamente en el **220/220** de los samples (sin variantes
  erróneas, sin duplicados, apertura al inicio y cierre al final del bloque).

---

## Distribución

### Tipos (33/33 cubiertos)

Énfasis en el núcleo (§1–§30): `HYPOTHESIS_GENERATION` (15), `HYPOTHESIS_REVISION` (9),
`FAILURE_AS_INFORMATION` (6), `ALTERNATIVE_PATHS` (5), `EVIDENCE_ANALYSIS` (7),
`FALSE_POSITIVE` (9), `FALSE_NEGATIVE` (7), `WRONG_CLAIM` (7), `ROOT_CAUSE` (8),
`VULNERABILITY_ANALYSIS` (8), `THREAT_MODELING` (8), `RED/BLUE/PURPLE_TEAM` (16),
`RISK_PRIORITIZATION` (7), `PENTEST_PLANNING` (8), `IMPACT_ANALYSIS` (6)…
más `WEB_SECURITY, API_SECURITY, NETWORK_ANALYSIS, HOST_SECURITY,
CODE_SECURITY_REVIEW, REVERSE_ENGINEERING, INCIDENT_ANALYSIS, LOG_ANALYSIS,
DETECTION, MITIGATION, RETEST, SECURITY_ARCHITECTURE, CTF, LAB_SCENARIO,
SECURITY_REASONING, ADVERSARIAL_REASONING`.

### Dificultad (§26: 10/20/35/25/10)

| Nivel | n | % |
|---|---|---|
| fundamentals | 22 | 10.0 % |
| intermediate | 42 | 19.1 % |
| advanced | 82 | 37.3 % |
| expert | 52 | 23.6 % |
| adversarial | 22 | 10.0 % |

---

## Principios didácticos incrustados

1. **Equivocarse ≠ razonar mal.** Hipótesis plausible → prueba → resultado negativo → nueva información → actualización (`FAILURE_AS_INFORMATION`, `HYPOTHESIS_REVISION`).
2. **Una puerta cerrada no cierra el edificio.** Cambiar de superficie con justificación (`ALTERNATIVE_PATHS`).
3. **El tercer intento puede cambiar la hipótesis** — pero cada intento aporta información nueva; prohibido repetir sin cambiar nada.
4. **Fail forward:** `FAIL → LEARN → ADAPT → RETRY DIFFERENTLY` (nunca random retry).
5. **Hipótesis múltiples** (H1/H2/H3…) actualizadas por evidencia; no casarse con la primera explicación plausible.
6. **NO ENCONTRADO ≠ NO EXISTE.**
7. **Evidencia clasificada:** OBSERVED / INFERRED / ASSUMED / UNKNOWN en cada análisis complejo.
8. **Causalidad:** síntoma → mecanismo → causa raíz → impacto; mitigación → cambio observable → retest.
9. **Red + Blue + Purple:** el razonamiento ofensivo orientado a defensa.
10. **Herramientas = instrumentos, no oráculos.** Primero la pregunta, después la herramienta.

## Errores penalizados en las respuestas del modelo

Confundir posibilidad con evidencia · exposición con vulnerabilidad · resultado
negativo con sistema seguro · insistir ciegamente con la misma prueba · ignorar
nueva evidencia · aferrarse a la primera hipótesis · declarar impacto sin
demostrarlo · usar una herramienta sin saber qué pregunta responde.

## Entornos y límites

- **Todos los escenarios** son laboratorios, CTF, simulaciones, toy programs o
  proyectos open source de práctica. **Ningún objetivo real de terceros.**
- Los payloads, cuando aparecen, son instrumentos de medición inofensivos
  (marcadores neutros, marcas reversibles), no cargas destructivas.
- Referencias metodológicas conceptuales: **OWASP WSTG**, **NIST SP 800-115**,
  **MITRE ATT&CK** (tácticas como vocabulario, no recetas).
- Regla de calidad aplicada: `QUALITY > DEPTH > DIVERSITY > QUANTITY`.

---

## Validación

```bash
python3 scripts/validate_ai_ku_brainstorming.py data/AI-ku_brainstorming.jsonl
```

Resultado actual: **220 samples · 0 errores · 0 avisos · 33/33 tipos · 19/20 dominios**.

## Licencia

Por definir por el propietario del proyecto AI-ku.
