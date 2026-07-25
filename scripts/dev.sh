#! /bin/bash

set -e
set -x

export ENV_FILE="${ENV_FILE:-.env.local}"
source "$ENV_FILE"

uvicorn app.main:app --host "$HOST" --port "$PORT" --reload

