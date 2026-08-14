import os

import httpx
from dotenv import load_dotenv

from schemas import GoogleBooks, WeatherResponse

load_dotenv()

if not os.getenv("GOOGLE_BOOKS_API_KEY"):
    print("warning: Check [GOOGLE_BOOKS_API_KEY")


async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )
    response.raise_for_status()
    data = response.json()
    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )


async def fetch_books(keyword: str, limit: int = 5) -> list[GoogleBooks]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": keyword,
                "maxResults": limit,
                "key": os.getenv("GOOGLE_BOOKS_API_KEY"),
            },
        )
        data = response.json()
        response.raise_for_status()

    result = []
    for item in data.get("items", []):
        book_info = item.get("volumeInfo", {})
        result.append(
            GoogleBooks(
                title=book_info.get("title", "No Title"),
                authors=book_info.get("authors", []),
                published_Date=book_info.get("publishedDate", "No Date"),
            )
        )

    return result
