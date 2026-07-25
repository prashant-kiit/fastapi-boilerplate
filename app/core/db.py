from fastapi import Request
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)


def get_session(request: Request):
    with Session(engine) as session:
        try:
            # request.state['db_session'] = session
            yield session
        except Exception:
            session.rollback()
            raise
