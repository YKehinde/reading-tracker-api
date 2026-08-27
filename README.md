# Reading Tracker API

A small FastAPI service for tracking books you're reading, backed by SQLite via SQLModel.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

Interactive docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path               | Description                        |
| ------ | ------------------ | ---------------------------------- |
| GET    | `/health`          | Health check                      |
| POST   | `/books`           | Create a book                     |
| GET    | `/books`           | List books (supports filtering)   |
| GET    | `/books/{book_id}` | Get a single book                 |
| PUT    | `/books/{book_id}` | Replace a book                    |
| PATCH  | `/books/{book_id}` | Partially update a book           |
| DELETE | `/books/{book_id}` | Delete a book                     |

## Tests

```bash
pytest
```
