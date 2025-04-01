from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User
from src.auth.schemas import UserCreateModel
from src.auth.utils import generate_password_hash


class UserAlreadyExists(Exception):
    pass


class UserService:
    UserAlreadyExists = UserAlreadyExists

    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        print(f"Before query - Session in transaction: {session.in_transaction()}")
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        print(f"After query - Session in transaction: {session.in_transaction()}")
        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return user is not None

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        async with session.begin():
            if await self.user_exists(user_data.email, session):
                raise UserAlreadyExists

            user_data_dict = user_data.model_dump()
            new_user = User(**user_data_dict)
            new_user.password_hash = generate_password_hash(user_data_dict['password'])
            session.add(new_user)
        return new_user
