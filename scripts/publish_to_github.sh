#!/usr/bin/env bash
# publish_to_github.sh — Publica el repo AI-ku_brainstorming en GitHub.
#
# USO:
#   GITHUB_TOKEN=ghp_xxx bash publish_to_github.sh
#
# - El token SOLO se usa como variable de entorno; nunca se escribe en disco,
#   ni en .git/config, ni en logs.
# - Crea el repositorio "AI-ku_brainstorming" bajo la cuenta del token
#   (si no existe ya) y hace push de la rama main.
# - Opcional: PUBLIC=0 para crear el repo privado (por defecto público).

set -euo pipefail

: "${GITHUB_TOKEN:?Falta GITHUB_TOKEN (p. ej. GITHUB_TOKEN=ghp_... bash publish_to_github.sh)}"
PUBLIC="${PUBLIC:-1}"
REPO_NAME="AI-ku_brainstorming"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API="https://api.github.com"

# Cabecera de autenticación (el token nunca se imprime)
auth() { curl -sS -H "Authorization: Bearer ${GITHUB_TOKEN}" \
              -H "Accept: application/vnd.github+json" "$@"; }

# 1) ¿Quién es el propietario?
USER_LOGIN="$(auth "${API}/user" | python3 -c "import json,sys;print(json.load(sys.stdin).get('login',''))")"
if [ -z "${USER_LOGIN}" ]; then echo "ERROR: token inválido o sin permiso (no se pudo leer /user)"; exit 1; fi
echo "Propietario: ${USER_LOGIN}"

# 2) ¿Existe ya el repo? Si no, crearlo.
STATUS="$(auth -o /dev/null -w '%{http_code}' "${API}/repos/${USER_LOGIN}/${REPO_NAME}")"
if [ "${STATUS}" = "200" ]; then
  echo "El repo ${USER_LOGIN}/${REPO_NAME} ya existe; se usará tal cual."
else
  PRIV="false"; [ "${PUBLIC}" = "0" ] && PRIV="true"
  CREATE="$(auth -X POST "${API}/user/repos" \
    -d "{\"name\":\"${REPO_NAME}\",\"description\":\"Dataset JSONL de razonamiento de pentester/ethical hacker (220 samples) para el Expert 177 de AI-ku — entornos autorizados (lab/CTF/simulación)\",\"private\":${PRIV},\"auto_init\":false}")"
  echo "Repo creado: ${USER_LOGIN}/${REPO_NAME}"
fi

# 3) Push usando credential helper efímero (el token NO queda en .git/config)
cd "${REPO_DIR}"
git -c credential.helper='!f() { echo "username=x-access-token"; echo "password=${GITHUB_TOKEN}"; }; f' \
    push "https://github.com/${USER_LOGIN}/${REPO_NAME}.git" main --force 1>&2

# 4) Topics descriptivos
auth -X PUT -o /dev/null "${API}/repos/${USER_LOGIN}/${REPO_NAME}/topics" \
  -d '{"names":["ai-dataset","jsonl","fine-tuning","security","pentesting","reasoning","ctf","threat-modeling"]}' || true

echo
echo "PUBLICADO: https://github.com/${USER_LOGIN}/${REPO_NAME}"
