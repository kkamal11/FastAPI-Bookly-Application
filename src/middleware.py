from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
import time
import logging
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

EXCLUDED_PATHS = ["/auth/login","/auth/register", "verify-email", "/auth/refresh-token"]

def register_middleware(app: FastAPI):
    
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        formatted_process_time = f"{process_time:.4f} seconds"
        
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} - completed in={formatted_process_time}"

        print(message)
                
        return response


    @app.middleware("http")
    async def authentication_middleware(request: Request, call_next):
        if any(p in request.url.path for p in EXCLUDED_PATHS):
            return await call_next(request)
        if any(p in request.url.path for p in ["/docs", "/redoc", "/openapi.json"]):
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
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*","localhost"]
    )

