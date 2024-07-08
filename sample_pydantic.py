from pydantic import BaseModel, Field, field_validator , ValidationError, constr,confloat, model_validator, model_serializer,field_serializer
from typing import Annotated, ClassVar
from enum import Enum
from datetime import datetime


def current_year() -> datetime.year:
    return datetime.now().year


class Author(BaseModel):
    name: str
    birth_date: Annotated[int,  Field(..., alias='birthDate')]


class Genre(str, Enum):
    fiction = "Fiction"
    nonFiction = "NonFiction"
    mystery = "Mystery"
    crime = "Crime"
    comedy = "Comedy"
    science = "Science"
    short_story = "ShortStory"
    thriller = "Thriller"


class Book(BaseModel):
    title: constr(min_length=1, max_length=50)
    author: list[Author] = Field(default_factory=list)
    pages: int
    price: confloat(gt=0) | None = None
    published_year: Annotated[int, Field(..., alias='publishedYear')]
    current_year: int = Field(default_factory=current_year, alias="currentYear")
    in_stock: Annotated[bool, Field(..., alias='InStock')]
    genre: Genre
    metadata: dict[str, str] = None

    max_pages_for_genre: ClassVar[dict[Genre, int]] = {
        Genre.short_story: 100,
        Genre.fiction: 1000,
        Genre.science: 700,
    }

    @field_serializer('genre')
    def custom_genre_output(self, genre: Genre):
        return genre.value

    @model_validator(mode='before')
    def check_price_and_metadata(cls, values):
        if values.get('price') is None and values.get('metadata') is None:
            raise ValueError('Either price or metadata should be provided.')
        return values

    @field_validator('in_stock')
    @classmethod
    def in_stock_validator(cls, value):
        if not value:
            raise ValueError('Book is not in stock')
        return value

    # @field_validator('pages')
    @model_validator(mode='after')
    def check_pages_for_genre(cls, values):
        if values is None:
            raise ValueError('values is none')
        genre = values.genre
        pages = values.pages
        max_pages = cls.max_pages_for_genre.get(genre.lower())
        if max_pages and pages > max_pages:
            raise ValueError(f"pages for {genre} should not exceeds {max_pages}")
        return values


data = {
    "title": "2000",
    "author": [
    {
        "name": 'weller',
        "birthDate": "2001"
    },
    {
        "name": "bob",
        'birthDate': "2002"
    },
    {
        "name": "John Doe",
        "birthDate": 1994
    }],
    "pages": 600,
    "price": "3.89",
    "publishedYear": 1999,
    "InStock": True,
    "genre": 'Science',
}


try:
    book = Book.model_validate(data)
    print(book.model_dump(exclude_none=True))
except ValidationError as e:
    print(e.json())

