from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import Book, BookCreateModel
from src.books.service import BookService
from src.database import get_session

book_router = APIRouter()
book_service = BookService()


@book_router.get('/', response_model=List[Book])
async def get_all_books(session: AsyncSession=Depends(get_session)):
    books = await book_service.get_all_books(session)
    return books


@book_router.post('/', status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book_data: BookCreateModel,session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data, session)
    return new_book
