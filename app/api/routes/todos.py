from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models import TodoCreate, TodoReplace, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/")
def get_todos(session: SessionDep):
    pass

@router.get("/{todo_id}")
def get_todo(todo_id: int, session: SessionDep):
    pass

@router.post("/")
def create_todo(todo: TodoCreate, session: SessionDep):
    pass

@router.put("/{todo_id}")
def replace_todo(todo_id: int, todo: TodoReplace, session: SessionDep):
    pass

@router.patch("/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate, session: SessionDep):
    pass

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, session: SessionDep):
    pass


