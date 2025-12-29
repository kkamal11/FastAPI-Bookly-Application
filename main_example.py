from fastapi import FastAPI
from fastapi import Header
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message":"Hello World"}

@app.get("/greet")
async def greet_name(name: Optional[str] = "User", age: int = -1) -> dict:
    return {"message": f"Hello, {name}!", "age": age}

class BookCreateModel(BaseModel):
    title: str
    author: str

@app.post("/create_book")
async def create_book(book: BookCreateModel) -> dict:
    return {"title": book.title, "author": book.author}

@app.get("/headers")
async def get_headers(
    accept : str = Header(None),
    accept_language : str = Header(None),
    user_agent : str = Header(None),
    host : str = Header(None),
    sec_ch_ua_platform : str = Header(None)) -> dict:
    request_headers = {}
    request_headers["Accept"] = accept  
    request_headers["Accept-language"] = accept_language
    request_headers["User-agent"] = user_agent
    request_headers["Host"] = host
    request_headers["Sec-ch-ua-platform"] = sec_ch_ua_platform
    return request_headers
