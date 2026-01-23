#!/usr/bin/env bash
set -e

ollama list | tail -n +2 | awk '{print $1}'
