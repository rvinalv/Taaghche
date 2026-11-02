from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///taaghche.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Create every table declared on ``SQLModel.metadata`` (idempotent)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: open one session per request and close it afterwards."""
    with Session(engine) as session:
        yield session
