#! /bin/bash

set -e
set -x

export ENV_FILE="${ENV_FILE:-.env.prod}"
source "$ENV_FILE"

uvicorn app.main:app --host "$HOST" --port "$PORT" --workers "${WORKERS:-4}"