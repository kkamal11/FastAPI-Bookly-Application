from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.books.router import book_router
from src.auth.router import auth_router
from src.reviews.router import review_router
from database.main import init_db
from config import env_config
from src.error import register_all_errors, register_internal_server_error_handler
from src.middleware import register_middleware

@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"=====Starting up the server=====")
    print("=====Initializing the database=====")
    await init_db()
    print("=====Database initialized=====")
    yield
    print(f"=====Shutting down the server=====")

version = env_config.API_VERSION

app = FastAPI(
    title="Bookly",
    description="A REST API for book review and rating service",
    version=version,
    # lifespan=life_span,
)

register_all_errors(app)
register_internal_server_error_handler(app)

register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])