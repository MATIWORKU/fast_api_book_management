from pydantic import BaseModel, field_validator, Field


class Book(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900, le=2024)

    @field_validator('title')
    def title_must_contain_at_least_one_word(cls, title: str):
        if len(title) < 1:
            return ValueError("Title must contain at least one word")
        return title
