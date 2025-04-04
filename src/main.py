from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.database import init_db
from src.errors import register_exception_handlers
from src.middleware import register_middleware

version = 'v1'


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print('Server is starting...')
    await init_db()
    yield
    print('Server is stopping...')


app = FastAPI(
    lifespan=lifespan,
    title='Bookly',
    description='A REST API for a book review web service',
    version=version,
)

register_exception_handlers(app)
register_middleware(app)

app.include_router(auth_router, prefix=f'/api/{version}/auth', tags=['auth'])
app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
