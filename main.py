from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.books.router import book_router
from src.auth.router import auth_router
from database.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"=====Starting up the server=====")
    print("=====Initializing the database=====")
    await init_db()
    print("=====Database initialized=====")
    yield
    print(f"=====Shutting down the server=====")

version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for book review and rating service",
    version=version,
    lifespan=life_span,
)


app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])