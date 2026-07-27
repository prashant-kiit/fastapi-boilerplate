import uuid
from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.api.routes import auth, todos
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logger import logger, request_id_ctx
from app.core.security import decode_access_token
from app.models import CustomException

PUBLIC_PATHS = {"/docs", "/openapi.json", "/redoc", "/auth/login"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"FastAPI Todo App is running at env {settings.ENVIRONMENT} at host http://{settings.HOST}:{settings.PORT}/v1"
    )
    yield
    # anything here runs on exit — this is "shutdown"
    logger.info(
        f"FastAPI Todo App shut down at env {settings.ENVIRONMENT} at host {settings.HOST} and port {settings.PORT}"
    )


async def on_startup_event():
    logger.info("Started")


async def on_shutdown_event():
    logger.info("Shut down")


app = FastAPI(
    title="FastAPI Todo App",
    root_path="/v1",
    on_startup=[on_startup_event],
    on_shutdown=[on_shutdown_event],
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def handle_request_interception(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    token = request_id_ctx.set(request.state.request_id)
    try:
        logger.info("Received request")
        if request.url.path not in PUBLIC_PATHS:
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content="Missing or invalid Authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            jwt_token = auth_header.removeprefix("Bearer ").strip()
            try:
                payload = decode_access_token(jwt_token)
            except jwt.ExpiredSignatureError:
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.InvalidTokenError:
                return Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            request.state.user_id = payload["sub"]
        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        logger.info("Sent request")
        return response
    finally:
        request_id_ctx.reset(token)


@app.exception_handler(RequestValidationError)
def handle_request_valdiation_exception(request: Request, exc: RequestValidationError):
    request_validation_exception_content = exc.errors()[0]["msg"]
    logger.exception(request_validation_exception_content)
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=request_validation_exception_content,
    )


@app.exception_handler(ResponseValidationError)
def handle_response_valdiation_exception(
    request: Request, exc: ResponseValidationError
):
    response_validation_exception_content = exc.errors()[0]["msg"]
    logger.exception(response_validation_exception_content)
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=response_validation_exception_content,
    )


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    # session = request.state.db_session
    # session.rollback()
    logger.exception("Todo with this title already exists")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Todo with this title already exists",
    )


@app.exception_handler(CustomException)
def handle_custom_exception(request: Request, exc: CustomException):
    logger.exception(exc.detail)
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)


@app.exception_handler(RateLimitExceeded)
def handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {exc.detail}")
    response = JSONResponse(
        {"error": f"Rate limit exceeded: {exc.detail}"},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    return request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )


app.include_router(auth.router)
app.include_router(todos.router)
