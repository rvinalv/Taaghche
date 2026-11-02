from sqlmodel import Field, Relationship, SQLModel


class Author(SQLModel, table=True):
    """A book author."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    country: str
    is_deleted: bool = Field(default=False)
    books: list["Book"] = Relationship(back_populates="author")


class Book(SQLModel, table=True):
    """A book that belongs to exactly one author."""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    year: int
    price: int
    author_id: int | None = Field(default=None, foreign_key="author.id")
    is_deleted: bool = Field(default=False)
    author: "Author" = Relationship(back_populates="books")


# --------------------------------------------------------------------------- #
# Author schemas
# --------------------------------------------------------------------------- #


class AuthorCreate(SQLModel):
    """Payload accepted when creating an author."""

    name: str = Field(min_length=1)
    country: str = Field(min_length=2)


class AuthorUpdate(SQLModel):
    """Payload accepted when partially updating an author (every field optional)."""

    name: str | None = Field(default=None, min_length=1)
    country: str | None = Field(default=None, min_length=2)


class AuthorResponse(SQLModel):
    """An author as returned to the client: exactly ``id``, ``name``, ``country``."""

    id: int
    name: str
    country: str


class AuthorList(SQLModel):
    """Envelope for a paginated author listing."""

    total: int
    items: list[AuthorResponse]
    page: int
    size: int

# --------------------------------------------------------------------------- #
# Book schemas
# --------------------------------------------------------------------------- #


class BookCreate(SQLModel):
    """Payload accepted when creating a book."""

    title: str = Field(min_length=1)
    year: int = Field(ge=1000, le=2100)
    price: int = Field(gt=0)
    author_id: int


class BookUpdate(SQLModel):
    """Payload accepted when partially updating a book (every field optional)."""

    title: str | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, ge=1000, le=2100)
    price: int | None = Field(default=None, gt=0)
    author_id: int | None = None


class BookResponse(SQLModel):
    """A book as returned to the client.

    Exactly ``id``, ``title``, ``year``, ``price`` and ``author_id``.
    """

    id: int
    title: str
    year: int
    price: int
    author_id: int | None = None


class BookList(SQLModel):
    """Envelope for a paginated book listing."""

    total: int
    items: list[BookResponse]
    page: int
    size: int


class AuthorWithBooks(AuthorResponse):
    """An author together with the (still alive) books they wrote."""

    books: list[BookResponse]
