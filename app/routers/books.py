from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from .. import repository
from ..db import get_session
from ..models import BookCreate, BookList, BookResponse, BookUpdate, Book

router = APIRouter(prefix="/books", tags=["books"])

SessionDep = Annotated[Session, Depends(get_session)]

BookSort = Literal[
    "title",
    "-title",
    "year",
    "-year",
    "price",
    "-price",
]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookResponse,
    include_in_schema=False,
)
def create_book(payload: BookCreate, session: SessionDep) -> BookResponse:
    """Create a new book."""
    author = repository.get_author(session, payload.author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    
    if repository.book_title_exists(session, payload.title, payload.author_id):
        raise HTTPException(status_code=409, detail="Author already has a book with this title")
        
    return repository.create_book(session, payload)



@router.get("/", response_model=BookList, include_in_schema=False)
@router.get("", response_model=BookList)
def list_books(
    session: SessionDep,
    author_id: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    q: str | None = None,
    sort: BookSort | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
) -> BookList:
    """List and search books with filtering, sorting and pagination."""
    total, items = repository.list_books(
        session,
        author_id=author_id,
        min_year=min_year,
        max_year=max_year,
        q=q,
        sort=sort,
        page=page,
        size=size,
    )
    return BookList(total=total, items=items, page=page, size=size)


@router.get("/{book_id}", response_model=BookResponse)
def read_book(book_id: int, session: SessionDep) -> BookResponse:
    """Read one book by id."""
    book = repository.get_book(session, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int, payload: BookUpdate, session: SessionDep
) -> BookResponse:
    """Partially update a book."""
    book = repository.update_book(session, book_id, payload)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: SessionDep) -> None:
    """Soft delete a book."""
    deleted = repository.delete_book(session, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")


@router.post("/{book_id}/restore", response_model=BookResponse)
def restore_book(book_id: int, session: SessionDep) -> BookResponse:
    """Restore a soft-deleted book."""
    book = repository.restore_book(session, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
