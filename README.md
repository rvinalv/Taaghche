# Taaghche API

A REST API built with **FastAPI** and **SQLModel** for managing authors and their books. It supports full CRUD, filtering, sorting, pagination, and soft deletion with restore.

## Features

- **Authors & books** — create, read, update, soft delete, and restore
- **Relationships** — every book belongs to an author; an author's books can be fetched with `GET /authors/{id}/books`
- **Soft delete** — `DELETE` marks a row as deleted instead of removing it; deleted rows are hidden from all reads and can be brought back with a `restore` endpoint
- **Filtering & search** — authors by country, books by author, year range, and title
- **Sorting** — on multiple fields in either direction
- **Pagination** — every listing returns `total`, `items`, `page`, and `size`
- **Validation** — constrained fields enforced by Pydantic, plus a uniqueness rule: an author cannot have two books with the same title
- **Auto-generated docs** — Swagger UI and ReDoc out of the box

## Tech stack

| Tool | Purpose |
| --- | --- |
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework |
| [SQLModel](https://sqlmodel.tiangolo.com/) | ORM + request/response schemas |
| [SQLite](https://www.sqlite.org/) | Database (`taaghche.db`, created automatically) |
| [uv](https://docs.astral.sh/uv/) | Package & environment management |
| Python 3.13+ | Runtime |

## Project structure

```
.
├── app/
│   ├── main.py            # App instance, table creation on startup, /health
│   ├── db.py              # Engine and per-request session dependency
│   ├── models.py          # Database tables and API schemas
│   ├── repository.py      # Data-access layer (CRUD, filters, sorting, pagination)
│   └── routers/
│       ├── authors.py     # /authors endpoints
│       └── books.py       # /books endpoints
├── pyproject.toml
└── README.md
```

## Getting started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Install

```bash
git clone <repository-url>
cd Taaghche
uv sync
```

### Run

```bash
uv run fastapi dev app/main.py
```

The server starts at <http://127.0.0.1:8000>. The SQLite database file `taaghche.db` and its tables are created automatically on startup.

Interactive docs:

- Swagger UI — <http://127.0.0.1:8000/docs>
- ReDoc — <http://127.0.0.1:8000/redoc>

## API reference

Base URL: `http://127.0.0.1:8000`

### Health

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe — returns `{"status": "ok"}` |

### Authors

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| `POST` | `/authors` | Create an author | `201` |
| `GET` | `/authors` | List authors (filter, sort, paginate) | `200` |
| `GET` | `/authors/{author_id}` | Get one author | `200` |
| `GET` | `/authors/{author_id}/books` | Get an author with their non-deleted books | `200` |
| `PATCH` | `/authors/{author_id}` | Partially update an author | `200` |
| `DELETE` | `/authors/{author_id}` | Soft delete an author | `204` |
| `POST` | `/authors/{author_id}/restore` | Restore a soft-deleted author | `200` |

**Author fields:** `id`, `name`, `country`.

**Create body:**

```json
{ "name": "Sadegh Hedayat", "country": "Iran" }
```

**Query parameters for `GET /authors`:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `country` | string | — | Case-insensitive partial match |
| `sort` | enum | `id` asc | `name`, `-name`, `country`, `-country` |
| `page` | int ≥ 1 | `1` | Page number |
| `size` | int ≥ 1 | `10` | Items per page |

**List response:**

```json
{ "total": 42, "items": [ { "id": 1, "name": "Sadegh Hedayat", "country": "Iran" } ], "page": 1, "size": 10 }
```

### Books

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| `POST` | `/books` | Create a book | `201` |
| `GET` | `/books` | List books (filter, search, sort, paginate) | `200` |
| `GET` | `/books/{book_id}` | Get one book | `200` |
| `PATCH` | `/books/{book_id}` | Partially update a book | `200` |
| `DELETE` | `/books/{book_id}` | Soft delete a book | `204` |
| `POST` | `/books/{book_id}/restore` | Restore a soft-deleted book | `200` |

**Book fields:** `id`, `title`, `year` (1000–2100), `price` (positive integer), `author_id`.

**Create body:**

```json
{ "title": "The Blind Owl", "year": 1937, "price": 250000, "author_id": 1 }
```

`POST /books` returns:

- `404` if the `author_id` does not refer to a non-deleted author
- `409` if that author already has a non-deleted book with the same title

**Query parameters for `GET /books`:**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `author_id` | int | — | Only books by this author |
| `min_year` | int | — | Published in or after this year |
| `max_year` | int | — | Published in or before this year |
| `q` | string | — | Case-insensitive partial title search |
| `sort` | enum | `id` asc | `title`, `-title`, `year`, `-year`, `price`, `-price` |
| `page` | int ≥ 1 | `1` | Page number |
| `size` | int ≥ 1 | `10` | Items per page |

**List response:**

```json
{
  "total": 1,
  "items": [ { "id": 1, "title": "The Blind Owl", "year": 1937, "price": 250000, "author_id": 1 } ],
  "page": 1,
  "size": 10
}
```

## Example requests

```bash
# Create an author
curl -X POST http://127.0.0.1:8000/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "Sadegh Hedayat", "country": "Iran"}'

# Create a book for that author
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "The Blind Owl", "year": 1937, "price": 250000, "author_id": 1}'

# Search books published between 1930 and 1950, sorted by year descending
curl "http://127.0.0.1:8000/books?min_year=1930&max_year=1950&sort=-year"

# Soft delete an author, then restore it
curl -X DELETE http://127.0.0.1:8000/authors/1
curl -X POST http://127.0.0.1:8000/authors/1/restore
```

## Behavior notes

- **Soft delete:** `DELETE` sets an internal `is_deleted` flag. Deleted authors and books are excluded from all GET/list results. Books that belong to a soft-deleted author remain visible in `/books`, but that author can no longer be retrieved or used to create new books.
- **Partial updates:** `PATCH` only changes fields present in the request body; omitted or `null` fields are left untouched.
- **Errors:** Not-found resources return `404` with a JSON `detail` message; duplicate book titles per author return `409`; invalid payloads return FastAPI's standard `422` validation error.
- **Database:** SQLite file lives at `taaghche.db` in the project root (ignored by git) and is created on first startup.
