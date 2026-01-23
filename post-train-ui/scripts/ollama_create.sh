#!/usr/bin/env bash
set -e

GGUF_NAME=$1
OLLAMA_NAME=$2

cat <<EOF > /models/Modelfile
FROM /models/${GGUF_NAME}
EOF

ollama create ${OLLAMA_NAME} -f /models/Modelfile
