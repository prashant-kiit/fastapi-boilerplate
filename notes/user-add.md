This is a **Dockerfile** snippet used to **run the container as a non-root user**, which is a production best practice.

```dockerfile
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### Line 1

```dockerfile
RUN useradd --create-home --uid 1000 appuser
```

* `useradd` → Creates a new Linux user.
* `--create-home` → Creates `/home/appuser`.
* `--uid 1000` → Assigns user ID `1000`.
* `appuser` → Username.

Equivalent to:

```bash
useradd -m -u 1000 appuser
```

---

```dockerfile
chown -R appuser:appuser /app
```

Changes the ownership of `/app` recursively.

* `-R` → Recursive
* `appuser:appuser` → Owner = `appuser`, Group = `appuser`

Without this, the new user might not have permission to read/write files in `/app`.

---

### Line 2

```dockerfile
USER appuser
```

From this point onward:

* All subsequent `RUN` commands execute as `appuser`.
* When the container starts, the application also runs as `appuser` instead of `root`.

For example:

```dockerfile
USER appuser

CMD ["python", "main.py"]
```

`python main.py` now runs as `appuser`.

---

### Why is this important?

Running containers as `root` is a security risk. If an attacker exploits your application, they gain root privileges inside the container, which can increase the impact of the compromise.

Running as a non-root user:

* Follows the **principle of least privilege**.
* Reduces the impact of security vulnerabilities.
* Satisfies security policies in many Kubernetes clusters and cloud platforms.

---

### Typical production Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This is the standard production pattern for FastAPI and most other application containers.
