#! /bin/bash

set -e
set -x

uvicorn app.main:app --port 8081 --reload

