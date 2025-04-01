from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer
from src.redis import add_jit_to_blocklist

from ..database import get_session
from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, verify_password

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserModel)
async def create_user(user_data: UserCreateModel, session: AsyncSession=Depends(get_session)) -> UserModel:
    try:
        new_user = await user_service.create_user(user_data, session)
    except user_service.UserAlreadyExists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='User with this email already exists.')
    return new_user


@auth_router.post('/signin')
async def login_user(login_data: UserLoginModel, session: AsyncSession=Depends(get_session)) -> JSONResponse:
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    print(f"After query get_user_by_email - Session in transaction: {session.in_transaction()}")
    if not (user and verify_password(password, user.password_hash)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect email or password.')

    access_token = create_access_token(
        user_data={'email': user.email, 'user_uid': str(user.uid)},
    )

    refresh_token = create_access_token(
        user_data={'email': user.email, 'user_uid': str(user.uid)},
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    return JSONResponse(
        content={
            'message': 'You are now logged in!',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {'email': user.email, 'uid': str(user.uid)},
        }
    )


@auth_router.post('/refresh_token')
async def get_new_access_token(
    token_data: dict = Depends(RefreshTokenBearer())
) -> JSONResponse:
    expiry_timestamp = token_data['exp']

    if datetime.fromtimestamp(expiry_timestamp) < datetime.now():
        new_access_token = create_access_token(user_data=token_data['user'])
        return JSONResponse(
            content={
                'message': 'New access token created.',
                'access_token': new_access_token,
            }
        )

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Invalid or expired token.')



@auth_router.get('/logout')
async def revoke_token(
    token_data: dict = Depends(AccessTokenBearer())
) -> JSONResponse:
    await add_jit_to_blocklist(token_data['jit'])
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'You are now logged out!',
        }
    )
