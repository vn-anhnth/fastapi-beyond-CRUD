from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.models import User
from src.auth.service import UserService
from src.auth.utils import decode_token
from src.database import get_session
from src.errors import AccessTokenRequired, InvalidToken, RefreshTokenRequired
from src.redis import is_jit_in_blocklist


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        creds = await super().__call__(request)

        token = creds.credentials

        if not self.is_token_valid(token):
            raise InvalidToken

        token_data = decode_token(token)

        if await is_jit_in_blocklist(token_data['jit']):
            raise InvalidToken

        self.verify_token_data(token_data)

        return token_data

    def is_token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError('Please override this method to verify token data.')


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data['refresh']:
            raise AccessTokenRequired


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data['refresh']:
            raise RefreshTokenRequired


async def get_current_user(
    token_data: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
) -> User | None:
    return await user_service.get_user_by_email(token_data['user']['email'], session)


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Please check your email for verification details.'
            )

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You are not allowed to access this action.'
            )
        return True
