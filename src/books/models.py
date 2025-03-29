import uuid
from datetime import date, datetime

from sqlmodel import TIMESTAMP, Column, Field, SQLModel


class Book(SQLModel, table=True):
    __tablename__ = 'books'

    # https://stackoverflow.com/questions/70172127/how-to-generate-a-uuid-field-with-fastapi-sqlalchemy-and-sqlmodel
    uid: uuid.UUID = Field(
        nullable=False, primary_key=True, default_factory=uuid.uuid4
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, default=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow))

    def __repr__(self) -> str:
        return f'<Book {self.title}>'
