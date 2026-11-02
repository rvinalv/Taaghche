from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import authors, books


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create the database tables when the application starts up."""
    create_db_and_tables()
    yield


app = FastAPI(title="Taaghche API", version="0.1.0", lifespan=lifespan)

app.include_router(authors.router)
app.include_router(books.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness probe, owned by the app itself and not by any router."""
    return {"status": "ok"}


# Also make sure the tables exist when the app is imported without the ASGI
# lifespan ever running (e.g. a test client that is not used as a context
# manager). Failures here must not stop the module from importing.
try:  # pragma: no cover - defensive
    create_db_and_tables()
except Exception:  # noqa: BLE001
    pass
