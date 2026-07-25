# fastapi-boilerplate

## Build cycle

### Setup (once, both envs)

```bash
pip install -r requirements-dev.txt -e .   # prod: pip install -r requirements.txt -e .
pre-commit install                         # dev-only: wires up git hooks from .pre-commit-config.yaml
```

`requirements.txt` and `requirements-dev.txt` are fully pinned lockfiles (direct + transitive deps), generated from `pyproject.toml` — don't hand-edit them.

### Dev cycle

```bash
bash scripts/format.sh    # ruff check --fix + ruff format + mypy — auto-fix lint/format, type-check
bash scripts/lint.sh      # ruff check + ruff format --check — check-only gate, used in CI
bash scripts/dev.sh       # loads .env.local, runs uvicorn with --reload for local iteration
```

### Build/package

```bash
python -m build           # uses [build-system] (hatchling) to produce dist/*.tar.gz and dist/*.whl
```

### Prod cycle

```bash
pip install -r requirements.txt -e .   # or: pip install dist/fastapi_boilerplate-*.whl
bash scripts/start.sh                  # loads .env.prod, runs uvicorn with multiple workers, no reload
```

There's no Dockerfile yet, so deploying today means running from source or installing the wheel built above — no containerized artifact.

### Updating dependencies

Edit `dependencies` / `optional-dependencies.dev` in `pyproject.toml`, then regenerate the lockfiles:

```bash
pip-compile pyproject.toml -o requirements.txt
pip-compile pyproject.toml --extra dev -o requirements-dev.txt
```

### Adding a new dependency

Example: adding Alembic (needed in both dev and prod, so it goes in `dependencies`, not the `dev` extra).

1. Add it to `dependencies` in `pyproject.toml`:
   ```toml
   dependencies = [
       "fastapi==0.139.2",
       ...
       "alembic==1.13.2",
   ]
   ```
   (Dev-only tools, e.g. a linter, go in `optional-dependencies.dev` instead.)

2. Regenerate both lockfiles so the pin and its transitive deps get resolved and recorded:
   ```bash
   pip-compile pyproject.toml -o requirements.txt
   pip-compile pyproject.toml --extra dev -o requirements-dev.txt
   ```

3. Install locally to pick up the change in your venv:
   ```bash
   pip install -r requirements-dev.txt -e .
   ```

4. Verify: e.g. `alembic --version`, and confirm `python -c "from app.main import app"` still works.
