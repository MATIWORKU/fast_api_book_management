import os.path

from fastapi import FastAPI, APIRouter, Path, Query, Form, File, UploadFile, status
from fastapi.responses import FileResponse
from typing import Annotated
import book_model
import shutil

# Basic Routing
app = FastAPI()
books = []
upload_dir = "./uploaded_files"

router = APIRouter(prefix="/books", tags=["books"])


@router.get('/')
async def root():
    return {"Welcome": "To your Book Management System."}


# Path Parameter
@router.get('/{book_id}')
async def get_book(book_id: Annotated[int, Path(ge=0, le=10)]):
    return {"book_id": books[book_id]}


# Query Parameter
@router.get('/search/')
async def search_book(q: Annotated[str | None, Query(pattern='h')]):
    if q:
        requested_book = [book for book in books if q.lower() in book["title"].lower()]
        return {"books": requested_book}
    return {"books": books}


# Request Body Parameter and Response Code
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_book(book: book_model.Book) -> list[book_model.Book]:
    title = book.title
    author = book.author
    year = book.year
    book = book_model.Book(title=title, author=author, year=year)
    books.append(book.dict())
    return books


# Response Body using pydantic
# @app.post('/book', response_model=Book)
# async def create_book(book: Book) -> Any:
#     return book


# Handling HTTP Methods
@router.put('/{book_id}')
async def update_book(book_id: Annotated[int, Path()], book: book_model.Book):
    if 0 <= book_id <= len(books):
        books[book_id] = book
    return {"message": "Book update successful", "book": book}


@router.delete('/{book_id}')
async def delete_book(book_id: Annotated[int, Path(...)]):
    if 0 <= book_id <= len(books):
        removed_book = books.pop(book_id)
        return {"message": "Book was deleted successfully", "book": removed_book}
    return {"message": "Book not found"}


# Form Data Submission
@router.post('/form')
async def create_book_form(title: Annotated[str, Form()], author: Annotated[str, Form()], year: int = Form()):
    book = book_model.Book(title=title, author=author, year=year)
    books.append(book.dict())
    return {"message": "Book added via form", "book": book}


# File Uploads
@router.post('/upload')
async def upload_file(file: UploadFile = File()):
    file_path = os.path.join(upload_dir, file.filename)
    with open(f"{file_path}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "File Uploaded Successfully", "file": file.filename}


# File download
@router.get('/download/{book_name}')
async def download_book(book_name: str):
    file_path = os.path.join(upload_dir, book_name)
    if not os.path.exists(file_path):
        return {"Error": "Path does not exist"}
    return FileResponse(file_path, filename=book_name, media_type="application/octet-stream")

app.include_router(router)
