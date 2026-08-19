import datetime

from pydantic import BaseModel, Field, field_validator


class Publisher(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    city: str = "seoul", Field(min_length=1, max_length=50)


class BookCreate(BaseModel):
    title: str = Field(min_length=0, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900, le=2050)
    tags: list[str] = Field(default_factory=list)
    publisher: Publisher | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip()  # 공백제거
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("year")
    @classmethod
    def year_check(cls, v: str) -> str:
        if v > datetime.datetime.now().year:
            raise ValueError("The year cannot be greater than the current year")
        return v

    @field_validator("tags")
    @classmethod
    def remove_duplicate_tags(cls, tags: list[str]) -> list[str]:
        return list(dict.fromkeys(tags))


class BookResponse(BookCreate):
    id: int


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    time: str


class GoogleBooks(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    published_Date: str = ""


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2100)
    tags: list[str] | None = None
    publisher: Publisher | None = None
