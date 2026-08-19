from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import books, external, system

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(system.router)
app.include_router(external.router)
app.include_router(books.router)
