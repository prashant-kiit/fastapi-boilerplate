import logging

from app.core.config import ENV_FILE
from app.core.context import request_id_ctx


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


logging.basicConfig(
    level=logging.INFO if ENV_FILE == ".env.prod" else logging.DEBUG,
    format="%(levelname)s:     %(request_id)s | %(message)s | %(asctime)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("fastapi-todo-app-logger")
logger.addFilter(RequestIdFilter())
