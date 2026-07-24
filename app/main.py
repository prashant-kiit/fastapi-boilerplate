from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import todos
from app.core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    # anything here runs on exit — this is "shutdown"


app = FastAPI(title="FastAPI Todo App", lifespan=lifespan)
app.include_router(todos.router)