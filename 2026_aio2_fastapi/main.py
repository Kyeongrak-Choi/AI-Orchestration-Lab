import asyncio
import time

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from external_api import fetch_books, fetch_weather
from schemas import BookCreate, BookResponse, BookUpdate, GoogleBooks, WeatherResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
    {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021},
    {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023},
    {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022},
    {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020},
    {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024},
]

params_value = {
    "latitude": "37.5168",
    "longitude": "126.7074",
    "current": "temperature_2m,relative_humidity_2m",
    "timezone": "Asia/Seoul",
}

url = "https://api.open-meteo.com/v1/forecast"


def get_book_or_404(book_id: int) -> dict:
    """번호로 도서를 찾고, 없으면 404를 발생시킨다."""
    for b in books:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="Not found book")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/info")
def info():
    return {"name": "Books Managing API", "version": "0.1.0"}


@app.get("/books", response_model=list[BookResponse])
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
def page_books(skip: int = 0, limit: int = 2):
    return books[skip : skip + limit]


@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(3)  # 비동기
    return {"type": "async", "message": "3초 대기 완료"}


@app.get("/slow-block")
async def slow_block():
    time.sleep(3)
    return {"type": "block", "message": "3초 대기 완료"}


# @app.get("/weather/raw")
# async def weather_raw():
# async with httpx.AsyncClient(timeout=5) as client:
#     response = await client.get(
#         url
#         , params = params_value
#     )
#     return response.json()


# @app.get("/weather", response_model=WeatherResponse)
# async def weather(latitude: float = 36.8, longitude: float = 127.1):
#     async with httpx.AsyncClient(timeout=5) as client:
#         response = await client.get(
#             url,
#             params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "current": "temperature_2m",
#             },
#         )

#     return WeatherResponse(
#         latitude=response.json()["latitude"],
#         longitude=response.json()["longitude"],
#         temperature=response.json()["current"]["temperature_2m"],
#         time=response.json()["current"]["time"],
#     )


@app.get("/weather", response_model=WeatherResponse)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    return await fetch_weather(latitude, longitude)


@app.get("/books/external", response_model=list[GoogleBooks])
async def searchExternalBooks(keyword: str = "파이썬", limit: int = 5):
    return await fetch_books(keyword, limit)


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    # title duplication block
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="Already exist book")
    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {"id": new_id, **book.model_dump()}
    books.append(new_book)
    return new_book


@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
    # for book in books:
    #     if book["id"] == book_id:
    #         return book
    # raise HTTPException(status_code=404, detail="Not Found Book")
    return get_book_or_404(book_id)


@app.put(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["Book"],
    summary="Update Book",
    responses={404: {"description": "Not Found Book"}},
)
def update_book(book_id: int, book: BookCreate):
    """
    도서 정보를 전체 교체합니다. 보내지 않은 필드는 기본값으로 바뀝니다.
    일부만 고치려면 PATCH를 사용하세요.
    """
    # for i, b in enumerate(books):
    #     if b["id"] == book_id:
    #         books[i] = {"id": book_id, **book.model_dump()}
    #         # Success
    #         return books[i]
    # # Fail
    # raise HTTPException(status_code=404, detail="Not found book")
    old = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old)] = new_book
    return new_book


@app.patch(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["book"],
    summary="update book part",
    responses={404: {"description": "Not found book"}},
)
def patch_book(book_id: int, patch: BookUpdate):
    """
    보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다.
    """
    # for b in books:
    #     if b["id"] == book_id:
    #         changes = patch.model_dump(exclude_unset=True)
    #         b.update(changes)
    #         return b
    # raise HTTPException(status_code=404, detail="Not found book")
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    return book


@app.delete(
    "/books/{book_id}",
    status_code=204,
    tags=["도서"],
    summary="도서 삭제",
    responses={404: {"description": "Not found book"}},
)
def delete_book(book_id: int):
    """
    도서를 삭제합니다. 성공 시 본문 없이 204를 반환합니다.
    """
    # for i, b in enumerate(books):
    #     if b["id"] == book_id:
    #         books.pop(i)
    #         return None
    # raise HTTPException(status_code=404, detail="Not found book")
    book = get_book_or_404(book_id)
    books.remove(book)