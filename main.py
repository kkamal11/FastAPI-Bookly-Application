from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from src.books.router import book_router
from src.auth.router import auth_router
from src.reviews.router import review_router
from database.main import init_db
from src.error import *

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
    # lifespan=life_span,
)

app.add_exception_handler(
    UserAlreadyExistsError, 
    create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "message": "User with this email already exists.",
            "error_code": "USER_ALREADY_EXISTS",
            "resolution": "Please use a different email."
        }
    )
)


app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])