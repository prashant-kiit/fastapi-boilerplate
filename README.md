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

## Database migrations (Alembic)

Schema changes go through Alembic, not `SQLModel.metadata.create_all()` — the app no longer creates tables on startup. Run migrations explicitly before starting the app against a fresh database:

```bash
.venv/bin/alembic upgrade head
```

`alembic/env.py` reads `DATABASE_URL` from `app.core.config.settings` (same `.env.local` / `.env.prod` / `ENV_FILE` resolution as the app itself), and imports `app.models` so every `SQLModel` table registers for autogenerate.

### Adding a new table

Example: adding a `Task` table.

1. Define the model in `app/models.py`:
   ```python
   class TaskBase(SQLModel):
       title: str = Field(min_length=1, max_length=100)
       # ... other fields

   class Task(TaskBase, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
   ```
   If you put the model in a new module instead of `app/models.py`, add an import for it in `alembic/env.py` too — autogenerate only sees tables that have actually been imported.

2. Generate the migration:
   ```bash
   .venv/bin/alembic revision --autogenerate -m "create task table"
   ```

3. Review the generated file in `alembic/versions/` — check column types, nullability, and defaults. Autogenerate can miss things (renames show up as drop+add) and can pick up unrelated diffs if your local DB isn't already at `head`, so run `alembic current` first if unsure.

4. Apply it:
   ```bash
   .venv/bin/alembic upgrade head
   ```

### Downgrading

```bash
.venv/bin/alembic downgrade -1       # undo the last migration
.venv/bin/alembic downgrade base     # undo everything
.venv/bin/alembic downgrade <rev>    # roll back to a specific revision
```

### Other useful commands

```bash
.venv/bin/alembic current    # revision the database is currently stamped at
.venv/bin/alembic history    # list all migrations
```

Point at a different database the same way the app does:

```bash
ENV_FILE=.env.prod .venv/bin/alembic upgrade head
# or
DATABASE_URL="sqlite:///./other.db" .venv/bin/alembic upgrade head
```
