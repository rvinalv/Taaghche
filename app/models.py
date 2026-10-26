from sqlmodel import SQLModel, Field, Relationship, ForeignKey



class Author(SQLModel, table = True):

    id: int | None = Field(primary_key=True, default=None)
    name: str
    country: str
    is_deleted: bool = False
    books: list["Book"] = Relationship(back_populates="author")


class Book(SQLModel, table = True):

    id: int | None = Field(primary_key=True, default=None)
    title: str
    year: int
    price: int
    author_id: int | None = Field(foreign_key="author.id")
    author: Author = Relationship(back_populates="books")


class AuthorResponse(SQLModel):

    id: int
    name: str
    country: str

class BookResponse(SQLModel):

    id: int
    title: str
    year: str
    price: int
    author_id: int

class AuthorCreateUpdate(SQLModel):

    name: str | None = Field(min_length=1, default=None)
    country: str | None = Field(min_length=2, default=None)

class BookCreateUpdate(SQLModel):

    title: str | None = Field(min_length=1, default=None)
    year: int | None = Field(gt=1000, lt=2100, default=None)
    price: int | None = Field(gt=0, default=None)

