from sqlmodel import Session, col, func, select

from .models import Author, AuthorCreate, AuthorUpdate, Book, BookCreate, BookUpdate

DEFAULT_PAGE_SIZE = 10


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _alive(model: type[Author] | type[Book]):
    """Condition matching rows that have not been soft deleted."""
    return model.is_deleted == False  # noqa: E712 - SQLAlchemy needs `==`, not `is`


# --------------------------------------------------------------------------- #
# Author CRUD
# --------------------------------------------------------------------------- #


def create_author(session: Session, data: AuthorCreate) -> Author:
    """Insert a new author and return the persisted row."""
    author = Author(**data.model_dump())
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def get_author(session: Session, author_id: int) -> Author | None:
    """Return a single non-deleted author, or ``None``."""
    statement = select(Author).where(_alive(Author), Author.id == author_id)
    return session.exec(statement).first()


def list_authors(
    session: Session,
    *,
    country: str | None = None,
    sort: str | None = None,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
) -> tuple[int, list[Author]]:
    """Return one page of authors plus the total number of matching authors."""
    conditions = [_alive(Author)]
    if country is not None:
        conditions.append(col(Author.country).ilike(f"%{country}%"))

    total_statement = select(func.count()).select_from(Author).where(*conditions)
    total = session.exec(total_statement).one()

    statement = select(Author).where(*conditions)
    statement = _apply_author_sort(statement, sort)
    statement = statement.offset((page - 1) * size).limit(size)
    items = list(session.exec(statement).all())

    return total, items


def _apply_author_sort(statement, sort: str | None):
    """Apply the requested ordering, defaulting to ascending ``id``."""
    match sort:
        case "name":
            return statement.order_by(col(Author.name).asc())
        case "-name":
            return statement.order_by(col(Author.name).desc())
        case "country":
            return statement.order_by(col(Author.country).asc())
        case "-country":
            return statement.order_by(col(Author.country).desc())
        case _:
            return statement.order_by(col(Author.id).asc())


def update_author(
    session: Session, author_id: int, data: AuthorUpdate
) -> Author | None:
    """Apply a partial update to a non-deleted author, or return ``None``."""
    author = get_author(session, author_id)
    if author is None:
        return None

    for field_name, value in data.model_dump(exclude_unset=True).items():
        # Skip omitted/empty values so PATCH stays partial.
        if value is not None:
            setattr(author, field_name, value)

    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def delete_author(session: Session, author_id: int) -> bool:
    """Soft delete an author, returning ``False`` when it is not found."""
    author = get_author(session, author_id)
    if author is None:
        return False

    author.is_deleted = True
    session.add(author)
    session.commit()
    return True


def restore_author(session: Session, author_id: int) -> Author | None:
    """Clear the soft-delete flag, so the author is visible again."""
    statement = select(Author).where(Author.id == author_id)
    author = session.exec(statement).first()
    if author is None:
        return None

    author.is_deleted = False
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def get_author_books(session: Session, author_id: int) -> list[Book]:
    """Return the non-deleted books of one author."""
    statement = (
        select(Book)
        .where(_alive(Book), Book.author_id == author_id)
        .order_by(col(Book.id).asc())
    )
    return list(session.exec(statement).all())


# --------------------------------------------------------------------------- #
# Book CRUD
# --------------------------------------------------------------------------- #


def create_book(session: Session, data: BookCreate) -> Book:
    """Insert a new book and return the persisted row."""
    book = Book(**data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def get_book(session: Session, book_id: int) -> Book | None:
    """Return a single non-deleted book, or ``None``."""
    statement = select(Book).where(_alive(Book), Book.id == book_id)
    return session.exec(statement).first()


def list_books(
    session: Session,
    *,
    author_id: int | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
) -> tuple[int, list[Book]]:
    """Return one page of books plus the total number of matching books."""
    conditions = [_alive(Book)]
    # `is not None` checks keep falsy-but-meaningful values (e.g. 0) working.
    if author_id is not None:
        conditions.append(Book.author_id == author_id)
    if min_year is not None:
        conditions.append(Book.year >= min_year)
    if max_year is not None:
        conditions.append(Book.year <= max_year)
    if q is not None:
        conditions.append(col(Book.title).ilike(f"%{q}%"))

    total_statement = select(func.count()).select_from(Book).where(*conditions)
    total = session.exec(total_statement).one()

    statement = select(Book).where(*conditions)
    statement = _apply_book_sort(statement, sort)
    statement = statement.offset((page - 1) * size).limit(size)
    items = list(session.exec(statement).all())

    return total, items


def _apply_book_sort(statement, sort: str | None):
    """Apply the requested ordering, defaulting to ascending ``id``."""
    match sort:
        case "title":
            return statement.order_by(col(Book.title).asc())
        case "-title":
            return statement.order_by(col(Book.title).desc())
        case "year":
            return statement.order_by(col(Book.year).asc())
        case "-year":
            return statement.order_by(col(Book.year).desc())
        case "price":
            return statement.order_by(col(Book.price).asc())
        case "-price":
            return statement.order_by(col(Book.price).desc())
        case _:
            return statement.order_by(col(Book.id).asc())


def update_book(session: Session, book_id: int, data: BookUpdate) -> Book | None:
    """Apply a partial update to a non-deleted book, or return ``None``."""
    book = get_book(session, book_id)
    if book is None:
        return None

    for field_name, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(book, field_name, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def delete_book(session: Session, book_id: int) -> bool:
    """Soft delete a book, returning ``False`` when it is not found."""
    book = get_book(session, book_id)
    if book is None:
        return False

    book.is_deleted = True
    session.add(book)
    session.commit()
    return True


def restore_book(session: Session, book_id: int) -> Book | None:
    """Clear the soft-delete flag, so the book is visible again."""
    statement = select(Book).where(Book.id == book_id)
    book = session.exec(statement).first()
    if book is None:
        return None

    book.is_deleted = False
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def book_title_exists(
    session: Session, title: str, author_id: int
) -> bool:
    statement = select(Book.id).where(
        _alive(Book),
        Book.title==title,
        Book.author_id == author_id
    )
    return session.exec(statement).first() is not None
