import uuid
from datetime import datetime

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = 'users'

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={'description': 'Unique identifier for the user account'},
        )
    )

    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    email: str

    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default='user'))
    is_verified: bool = False
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow))

    def __repr__(self) -> str:
        return f'<User {self.username}>'
