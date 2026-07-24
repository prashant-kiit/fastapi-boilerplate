from sqlmodel import Session, SQLModel, create_engine

engine = create_engine("sqlite:///./todo.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session