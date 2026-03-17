#!/usr/bin/env bash
set -euo pipefail

IMAGES_DIR=${IMAGES_DIR:-/data/images}
OUT_DIR=${OUT_DIR:-/data/outputs}
TOPIC_THEMES=${TOPIC_THEMES:-"space,science,history,technology,curiosity"}
DURATION=${DURATION:-60}
PRIVACY=${PRIVACY:-public}
TTS=${TTS:-hf}\nHF_TTS_MODEL=${HF_TTS_MODEL:-facebook/mms-tts-eng}

YOUTUBE_TOKEN_FILE=${YOUTUBE_TOKEN_FILE:-/data/yt_token.json}
YOUTUBE_CLIENT_SECRETS_FILE=${YOUTUBE_CLIENT_SECRETS_FILE:-/data/client_secrets.json}

mkdir -p "${IMAGES_DIR}" "${OUT_DIR}"

# Write YouTube token/secret files from env if provided
if [[ -n "${YOUTUBE_TOKEN_JSON:-}" ]]; then
  echo "${YOUTUBE_TOKEN_JSON}" > "${YOUTUBE_TOKEN_FILE}"
fi

if [[ -n "${YOUTUBE_CLIENT_SECRETS_JSON:-}" ]]; then
  echo "${YOUTUBE_CLIENT_SECRETS_JSON}" > "${YOUTUBE_CLIENT_SECRETS_FILE}"
fi

# Optionally download images zip
if [[ -n "${IMAGES_ZIP_URL:-}" ]]; then
  if ! ls -1 "${IMAGES_DIR}"/* >/dev/null 2>&1; then
    echo "[start] downloading images..."
    curl -L "${IMAGES_ZIP_URL}" -o /tmp/images.zip
    unzip -q /tmp/images.zip -d "${IMAGES_DIR}"
    rm -f /tmp/images.zip
  fi
fi

cmd=(python main.py \
  --topic auto \
  --themes "${TOPIC_THEMES}" \
  --duration "${DURATION}" \
  --schedule \
  --loop \
  --upload \
  --privacy "${PRIVACY}" \
  --tts "${TTS}" \
  --images-dir "${IMAGES_DIR}" \
  --out-dir "${OUT_DIR}")

exec "${cmd[@]}"

