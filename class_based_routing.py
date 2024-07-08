# I created this file so i could work on class based(object-oriented) routing and also keep the main file


import os.path

from fastapi import FastAPI, APIRouter, Path, Query, Form, File, UploadFile, status
from fastapi.responses import FileResponse
from typing import Annotated
import shutil
import book_model


# Basic Routing
app = FastAPI()
upload_dir = "./uploaded_files"


class BookManager:
    def __init__(self):
        self.books = []
        self.router = APIRouter(prefix="/books", tags=["books"])
        self.define_routes()

    def define_routes(self):

        @self.router.get('/')
        async def root():
            return {"Welcome": "To your Book Management System."}

        # Path Parameter
        @self.router.get('/{book_id}')
        async def get_book(book_id: Annotated[int, Path(ge=0, le=10)]):
            return {f'{book_id}': self.books[book_id]}

        # Query Parameter
        @self.router.get('/search/')
        async def search_book(q: Annotated[str | None, Query(pattern='e')]):
            if q:
                requested_book = [book for book in self.books if q.lower() in book["title"].lower()]
                return {"books": requested_book}
            return {"books": self.books}

        # Request Body Parameter and Response Code
        @self.router.post('/', status_code=status.HTTP_201_CREATED)
        async def create_book(book: book_model.Book) -> list[book_model.Book]:
            self.books.append(book.dict())
            return self.books

        # Handling HTTP Methods
        @self.router.put('/{book_id}')
        async def update_book(book_id: Annotated[int, Path()], book: book_model.Book):
            if 0 <= book_id <= len(self.books):
                self.books[book_id] = book
            return {"message": "Book update successful", "book": book}

        @self.router.delete('/{book_id}')
        async def delete_book(book_id: Annotated[int, Path(...)]):
            if 0 <= book_id <= len(self.books):
                removed_book = self.books.pop(book_id)
                return {"message": "Book was deleted successfully", "book": removed_book}
            return {"message": "Book not found"}

        # Form Data Submission
        @self.router.post('/form')
        async def create_book_form(title: Annotated[str, Form()], author: Annotated[str, Form()], year: int = Form()):
            book = book_model.Book(title=title, author=author, year=year)
            self.books.append(book.dict())
            return {"message": "Book added via form", "book": book}

        # File Uploads
        @self.router.post('/upload')
        async def upload_file(file: UploadFile = File()):
            file_path = os.path.join(upload_dir, file.filename)
            with open(f"{file_path}", "wb") as f:
                shutil.copyfileobj(file.file, f)
            return {"message": "File Uploaded Successfully", "file": file.filename}

        # File download
        @self.router.get('/download/{book_name}')
        async def download_book(book_name: str):
            file_path = os.path.join(upload_dir, book_name)
            if not os.path.exists(file_path):
                return {"Error": "Path does not exist"}
            return FileResponse(file_path, filename=book_name, media_type="application/octet-stream")


book_manager = BookManager()

app.include_router(book_manager.router)
