from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from ..database import get_session
from .schemas import UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, verify_password

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


REFRESH_TOKEN_EXPIRY = 2


@auth_router.post('/signin')
async def login_user(login_data: UserLoginModel, session: AsyncSession=Depends(get_session)):
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
