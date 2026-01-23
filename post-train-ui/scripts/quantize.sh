#!/usr/bin/env bash
set -e

GGUF_NAME=$1
QTYPE=$2

cd /llama.cpp

./quantize \
  /models/${GGUF_NAME} \
  /models/${GGUF_NAME%.gguf}-${QTYPE}.gguf \
  ${QTYPE}
