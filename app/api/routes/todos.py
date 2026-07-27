from datetime import date

from fastapi import APIRouter, Request, status
from sqlmodel import col, select

from app.api.deps import SessionDep
from app.core.limiter import limiter
from app.core.logger import logger
from app.models import (
    CustomException,
    Todo,
    TodoCreate,
    TodoIdOnly,
    TodoStatus,
    TodoUpdate,
)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[Todo], status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def get_todos(request: Request, session: SessionDep):
    db_todos = session.exec(
        select(Todo).order_by(col(Todo.target_date)).limit(10)
    ).all()
    logger.info("Fetched Todos")
    return db_todos


@router.get("/search", response_model=list[Todo], status_code=status.HTTP_200_OK)
def search_todo(key: str, session: SessionDep):
    return session.exec(
        select(Todo).where(Todo.title == key or Todo.status == TodoStatus(key))
    ).all()


@router.get("/search-title", response_model=Todo, status_code=status.HTTP_200_OK)
def search_todo_by_title(title: str, session: SessionDep):
    todo = session.exec(select(Todo).where(Todo.title == title)).first()
    if not todo:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return todo


@router.get("/search-target-date", response_model=list[Todo])
def search_todo_by_target(target_date: date, session: SessionDep):
    """
    col() only purpose is to change the static type that pyright/basedpyright sees: i
    t takes the annotated field type (e.g. date) and returns something typed as a SQLAlchemy ColumnElement,
    which is what .order_by(), .where(), etc. expect in their type signatures.
    """
    return session.exec(
        select(Todo)
        .where(Todo.target_date >= target_date)
        .order_by(col(Todo.target_date))
    ).all()


@router.get("/search-status", response_model=list[Todo])
def search_todo_by_status(status: TodoStatus, session: SessionDep):
    return session.exec(select(Todo).where(Todo.status == status)).all()


@router.get("/{todo_id}", response_model=Todo)
def get_todo_by_id(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return todo


@router.post("/", response_model=TodoIdOnly, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, session: SessionDep):
    db_todo = Todo.model_validate(todo)
    session.add(db_todo)
    session.commit()
    logger.info(f"Todo created id {db_todo.id}")
    session.refresh(db_todo)
    return db_todo


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(todo_id: int, todo: TodoUpdate, session: SessionDep):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db_todo.sqlmodel_update(todo.model_dump())
    session.add(db_todo)
    session.commit()
    logger.info(f"Todo updated id {db_todo.id}")
    session.refresh(db_todo)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: SessionDep):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    session.delete(db_todo)
    session.commit()
    logger.info(f"Todo deleted id {db_todo.id}")
