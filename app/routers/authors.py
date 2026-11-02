from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from .. import repository
from ..db import get_session
from ..models import (
    AuthorCreate,
    AuthorList,
    AuthorResponse,
    AuthorUpdate,
    AuthorWithBooks,
    BookResponse,
)

router = APIRouter(prefix="/authors", tags=["authors"])

SessionDep = Annotated[Session, Depends(get_session)]

AuthorSort = Literal["name", "-name", "country", "-country"]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AuthorResponse)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthorResponse,
    include_in_schema=False,
)
def create_author(payload: AuthorCreate, session: SessionDep) -> AuthorResponse:
    """Create a new author."""
    return repository.create_author(session, payload)


@router.get("/", response_model=AuthorList, include_in_schema=False)
@router.get("", response_model=AuthorList)
def list_authors(
    session: SessionDep,
    country: str | None = None,
    sort: AuthorSort | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> AuthorList:
    """List authors, optionally filtered by country, with sorting and pagination."""
    total, items = repository.list_authors(
        session,
        country=country,
        sort=sort,
        page=page,
        size=size,
    )
    return AuthorList(total=total, items=items, page=page, size=size)


@router.get("/{author_id}", response_model=AuthorResponse)
def read_author(author_id: int, session: SessionDep) -> AuthorResponse:
    """Read one author by id."""
    author = repository.get_author(session, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.get("/{author_id}/books", response_model=AuthorWithBooks)
def read_author_with_books(author_id: int, session: SessionDep) -> AuthorWithBooks:
    """Read one author together with the books written by them."""
    author = repository.get_author(session, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")

    books = repository.get_author_books(session, author_id)
    return AuthorWithBooks(
        id=author.id,
        name=author.name,
        country=author.country,
        books=[BookResponse.model_validate(book) for book in books],
    )


@router.patch("/{author_id}", response_model=AuthorResponse)
def update_author(
    author_id: int, payload: AuthorUpdate, session: SessionDep
) -> AuthorResponse:
    """Partially update an author."""
    author = repository.update_author(session, author_id, payload)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, session: SessionDep) -> None:
    """Soft delete an author."""
    deleted = repository.delete_author(session, author_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Author not found")


@router.post("/{author_id}/restore", response_model=AuthorResponse)
def restore_author(author_id: int, session: SessionDep) -> AuthorResponse:
    """Restore a soft-deleted author."""
    author = repository.restore_author(session, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author
