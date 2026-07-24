from fastapi import Request
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine("sqlite:///./todo.db")


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session(request: Request):
    with Session(engine) as session:
        try:
            # request.state['db_session'] = session
            yield session
        except Exception:
            session.rollback()
            raise
