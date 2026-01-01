from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import time
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from logger.app_logger import app_logger
from logger.user_logger import get_user_logger


EXCLUDED_PATHS = ["/test","/auth/login","/auth/register", "verify-email", "/auth/refresh-token"]

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        client = request.client
        client_info = f"{client.host}:{client.port}" if client else "unknown"

        message = (
            f"{client_info} | "
            f"{request.method} | "
            f"{request.url.path} | "
            f"{response.status_code} | "
            f"{process_time:.4f}s"
        )

        app_logger.info(message)

        user = getattr(request.state, "user", None)
        if user:
            user_logger = get_user_logger(user.username)
            user_logger.info(
                f"{request.method} {request.url.path} "
                f"-> {response.status_code} "
                f"in {process_time:.4f}s"
            )

        return response


def register_middleware(app: FastAPI):
    
    """
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        formatted_process_time = f"{process_time:.4f} seconds"
        
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} - completed in={formatted_process_time}"

        print(message)
                
        return response
    """

    @app.middleware("http")
    async def authentication_middleware(request: Request, call_next):
        if "/test" in request.url.path:
            return await call_next(request)
        if any(p in request.url.path for p in EXCLUDED_PATHS):
            return await call_next(request)
        if any(p in request.url.path for p in ["/test","/docs", "/redoc", "/openapi.json"]):
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                content={
                    "message": "Not Authenticated",
                    "resolution": "Please provide valid authentication credentials."
                }
            )
        response = await call_next(request)
        return response
    app.add_middleware(
        LoggingMiddleware
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["bookly-api-f3af.onrender.com","localhost"]
    )