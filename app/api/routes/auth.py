from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.config import settings
from app.core.security import create_access_token, verify_identifier, verify_password
from app.models import CustomException, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # Compare against hashed demo credentials until a real user store exists.
    valid_username = verify_identifier(form_data.username, settings.DEMO_USERNAME_HASH)
    valid_password = verify_password(form_data.password, settings.DEMO_PASSWORD_HASH)
    if not (valid_username and valid_password):
        raise CustomException(
            status.HTTP_401_UNAUTHORIZED, "Incorrect username or password"
        )
    access_token = create_access_token(subject=form_data.username)
    return Token(access_token=access_token)
