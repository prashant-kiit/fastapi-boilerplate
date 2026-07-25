import logging

from app.core.config import ENV_FILE

logging.basicConfig(
    level=logging.INFO if ENV_FILE == "prod" else logging.DEBUG,
    format="%(levelname)s:     %(message)s | %(asctime)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("fastapi-todo-app-logger")
