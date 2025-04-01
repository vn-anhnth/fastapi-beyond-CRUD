import logging
import sys
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# logger = logging.getLogger('uvicorn.access')
# logger.disabled = True


def register_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def custom_logging_middleware(request: Request, call_next) -> Response:
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f'✅ Completed in {processing_time:.2f}s'
        print(message)
        sys.stdout.flush()

        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=['localhost', '127.0.0.1'],
    )
