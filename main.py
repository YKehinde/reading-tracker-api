from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import or_

# Book is now the actual database table — `table=True` tells SQLModel this
# class maps onto a real SQL table, not just a request/response shape.
# id is optional here because SQLite assigns it when a row is inserted;
# we don't know it until after we save.
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
    # Note: this is a plain `str` here, not `Literal[...]`. SQLite has no
    # concept of an enum column — that constraint only makes sense at the
    # API boundary, which is what BookCreate/BookUpdate are for below.
    status: str
    rating: int | None = None

# What a client sends us to create a book — no id, because the client
# shouldn't get to invent one. The server (well, the database) owns that.
class BookCreate(SQLModel):
    title: str
    author: str
    status: Literal["to_read", "reading", "finished"]
    rating: int | None = None

# What a client sends us for a partial update (PATCH) — every field optional.
class BookUpdate(SQLModel):
    title: str | None = None
    author: str | None = None
    status: Literal["to_read", "reading", "finished"] | None = None
    rating: int | None = None


# The engine is the thing that knows how to talk to the actual database file.
# "sqlite:///books.db" creates/opens a file called books.db next to main.py —
# this is the bit that gives us persistence across restarts.
engine = create_engine("sqlite:///books.db")


# A dependency: FastAPI calls this for us on every request that asks for it,
# hands the endpoint a fresh Session, and closes it afterwards — same idea
# as a request-scoped "give me a fresh connection, clean it up when you're
# done" pattern you'd recognise from other frameworks.
def get_session():
    with Session(engine) as session:
        yield session


# Runs once when the app starts up (before "yield") and once when it shuts
# down (after "yield"). We use it here to make sure the books table exists.
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Reading Tracker API", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Converted as a worked example ---
@app.post("/books", status_code=201)
def add_book(book: BookCreate, session: Session = Depends(get_session)):
    new_book = Book.model_validate(book)  # BookCreate -> Book, id left unset
    session.add(new_book)
    session.commit()
    session.refresh(new_book)  # pulls the id SQLite just assigned
    return new_book


# --- Converted as a worked example ---
@app.get("/books/{book_id}")
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404)
    return book


# --- Converted ---
@app.get("/books")
def list_books(
    status: Literal["to_read", "reading", "finished"] | None = None,
    search: str | None = None,
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
):
    query = select(Book)
    if status is not None:
        query = query.where(Book.status == status)
    if search is not None:
        query = query.where(or_(Book.title.ilike(f"%{search}%"), Book.author.ilike(f"%{search}%")))
    query = query.limit(limit).offset(offset)

    return session.exec(query).all()


# --- Converted ---
@app.delete("/books/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()


# --- Converted ---
@app.put("/books/{book_id}")
def replace_book(book_id: int, book: BookCreate, session: Session = Depends(get_session)):
    retrieved_book = session.get(Book, book_id)
    if retrieved_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    retrieved_book.title = book.title
    retrieved_book.author = book.author
    retrieved_book.status = book.status
    retrieved_book.rating = book.rating

    session.commit()
    session.refresh(retrieved_book)

    return retrieved_book


# --- Converted ---
@app.patch("/books/{book_id}")
def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_update.model_dump(exclude_unset=True).items():
        setattr(book, key, value)
    session.commit()
    session.refresh(book)

    return book
