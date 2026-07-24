#! /bin/bash

set -e
set -x

mypy app
ruff check app --fix
ruff format app