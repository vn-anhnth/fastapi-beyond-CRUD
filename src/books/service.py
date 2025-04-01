from typing import List

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.models import Book
from src.books.schemas import BookCreateModel, BookUpdateModel


class BookService:
    async def get_all_books(self, session: AsyncSession) -> List[Book]:
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_uid(self, book_uid: str, session: AsyncSession) -> Book | None:
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession) -> Book:
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        # new_book.published_date = datetime.strptime(book_data_dict['published_date'], '%Y-%m-%d')

        session.add(new_book)
        await session.commit()

        return new_book

    async def update_book_by_uid(self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession) -> Book | None:
        book_to_update = await self.get_book_by_uid(book_uid, session)
        if not book_to_update:
            return None

        update_data_dict = update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(book_to_update, k, v)

        await session.commit()

        return book_to_update

    async def delete_book_by_uid(self, book_uid: str, session: AsyncSession) -> bool:
        book_to_delete = await self.get_book_by_uid(book_uid, session)
        if not book_to_delete:
            return None

        await session.delete(book_to_delete)
        await session.commit()

        return True
