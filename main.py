import os.path

from fastapi import FastAPI, Query, Path, Form, File, UploadFile, status
from fastapi.responses import FileResponse, Response
from typing import Annotated, Any
from pydantic import BaseModel, Field, validator
import shutil

# Basic Routing
app = FastAPI()
books = []
upload_dir = "./uploaded_files"


@app.get('/')
async def root():
    return {"Welcome": "To your Book Management System."}


# Path Parameter
@app.get('/books/{book_id}')
async def get_book(book_id: Annotated[int, Path(ge=1, le=10)]):
    return {"book_id": books[book_id]}


# Query Parameter
@app.get('/books/search/')
async def search_book(q: Annotated[str | None, Query(pattern='book')]):
    if q:
        requested_book = [book for book in books if q.lower() in book["title"].lower()]
        return {"books": requested_book}
    return {"books": books}


# Request Body Parameter and Response Code
class Book(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900, le=2024)

    @validator('title')
    def title_must_contain_at_least_one_word(cls, title: str):
        if len(title) < 1:
            return ValueError("Title must contain at least one word")
        return title


@app.post('/books', status_code=status.HTTP_201_CREATED)
async def create_book(book: Book) -> list[Book]:
    books.append(book.dict())
    return books


# Response Body using pydantic
# @app.post('/book', response_model=Book)
# async def create_book(book: Book) -> Any:
#     return book


# Handling HTTP Methods
@app.put('/books/{book_id}')
async def update_book(book_id: Annotated[int, Path()], book: Book):
    if 0 <= book_id <= len(books):
        books[book_id] = book
    return {"message": "Book update successful", "book": book}


@app.delete('/books/{book_id}')
async def delete_book(book_id: Annotated[int, Path(...)]):
    if 0 <= book_id <= len(books):
        removed_book = books.pop(book_id)
        return {"message": "Book was deleted successfully", "book": removed_book}
    return {"message": "Book not found"}


# Form Data Submission
@app.post('/books/form')
async def create_book_form(title: Annotated[str, Form()], author: Annotated[str, Form()], year: int = Form()):
    book = Book(title=title, author=author, year=year)
    books.append(book.dict())
    return {"message": "Book added via form", "book": book}


# File Uploads
@app.post('/upload')
async def upload_file(file: UploadFile = File()):
    file_path = os.path.join(upload_dir, file.filename)
    with open(f"{file_path}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "File Uploaded Successfully", "file": file.filename}


# File download
@app.get('/download/{book_name}')
async def download_book(book_name: str):
    file_path = os.path.join(upload_dir, book_name)
    if not os.path.exists(file_path):
        return {"Error": "Path does not exist"}
    return FileResponse(file_path, filename=book_name, media_type="application/octet-stream")
