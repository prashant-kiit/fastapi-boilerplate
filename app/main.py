from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.api.routes import todos
from app.core.config import settings
from app.core.db import init_db
from app.models import CustomException


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"FastAPI Todo App is running at env {settings.ENVIRONMENT} at host {settings.HOST} and port {settings.PORT}"
    )
    init_db()
    yield
    # anything here runs on exit — this is "shutdown"


app = FastAPI(title="FastAPI Todo App", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
def handle_request_valdiation_exception(request: Request, exc: RequestValidationError):
    request_validation_exception_content = exc.errors()[0]["msg"]
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=request_validation_exception_content,
    )


@app.exception_handler(ResponseValidationError)
def handle_response_valdiation_exception(
    request: Request, exc: ResponseValidationError
):
    response_validation_exception_content = exc.errors()[0]["msg"]
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=response_validation_exception_content,
    )


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    # session = request.state.db_session
    # session.rollback()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Todo with this title already exists",
    )


@app.exception_handler(CustomException)
def handle_custom_exception(request: Request, exc: CustomException):
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


app.include_router(todos.router)
