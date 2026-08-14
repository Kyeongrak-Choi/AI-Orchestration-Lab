from fastapi import FastAPI, status, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import asyncio
import time
import httpx


class Publisher(BaseModel):
    name : str = Field(min_length = 1, max_length = 100)
    city : str = "seoul", Field(min_length = 1, max_length = 50)


class BookCreate(BaseModel):
    title: str = Field(min_length = 0, max_length = 100)
    author: str = Field(min_length = 1, max_length = 50)
    year: int = Field(ge = 1900, le = 2050)
    tags : list[str] = Field(default_factory = list)
    publisher : Publisher | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        v = v.strip() # 공백제거
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("year")
    @classmethod
    def year_check(cls, v: str) -> str:
        if v > datetime.now().year:
            raise ValueError("The year cannot be greater than the current year")
        return v

    @field_validator("tags")
    @classmethod
    def remove_duplicate_tags(cls, tags: list[str]) -> list[str]:
        return list(dict.fromkeys(tags))


class BookResponse(BookCreate):
    id: int


'''  
    test Case
    1. 새로운책 등록
    2. 북 목록 조회
    3. 등록한 책 검색 
'''

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year":2024},
]

params_value = {
    "latitude" : "37.5168"
    , "longitude" : "126.7074"
    , "current" : "temperature_2m,relative_humidity_2m"
    , "timezone" : "Asia/Seoul"
}

url ="https://api.open-meteo.com/v1/forecast"


# GET
@app.get("/health")
def health():
    return {"status" : "healthy"}

@app.get("/info")
def info():
    return {"name" : "Books Managing API", "version": "0.1.0"}

@app.get("/books"
         , response_model=list[BookResponse])
def list_books():
    return books

@app.get("/books/search")
def search_books(keyword: str = ""):
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]

@app.get("/books/filter")
def filter_books(author: str = "", sort: str = ""):
    result = books
    if author:
        result = [b for b in result if b["author"] == author]
    if sort == "year":
        result = sorted(result, key=lambda b: b["year"])
    return result

@app.get("/books/page")
def page_books(skip: int=0, limit: int=2):
    return books[skip: skip + limit]

@app.get("/books/{book_id}"
         , response_model = BookResponse)
def read_book(book_id:int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code = 404
                        , detail = "not Found Book")

@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3) # 비동기
    return {"type": "async","message": "3초 대기 완료"}

@app.get("/slow-block")
async def slow_block():
    time.sleep(3)
    return {"type": "block","message": "3초 대기 완료"}

@app.get("/weather/raw")
async def weather_raw():
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(
            url
            , params = params_value
        )
        return response.json()


# POST
@app.post("/books"
          , response_model = BookResponse
          , status_code = status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    # title duplication block
    for b in books:
        if b['title'] == book.title:
            raise HTTPException(status_code = 409, detail="Already exist book")
    new_id = max([b["id"] for b in books], default = 0) + 1
    new_book = {"id": new_id,**book.model_dump()}
    books.append(new_book)
    return new_book