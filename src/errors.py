from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    '''Base exception for all Bookly exceptions'''
    pass


class InvalidToken(BooklyException):
    '''User provided an invalid token'''
    pass


class AccessTokenRequired(BooklyException):
    '''User provided a refresh token instead of an access token'''
    pass


class RefreshTokenRequired(BooklyException):
    '''User provided an access token instead of a refresh token'''
    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BooklyException) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content=initial_detail
        )
    return exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status.HTTP_401_UNAUTHORIZED,
            {
                'error': 'This token is expired or invalid.',
                'resolution': 'Please get new token.',
                'error_code': 'invalid_token',
            }
        )
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                'message': 'Please provide a valid access token',
                'resolution': 'Please get an access token',
                'error_code': 'access_token_required',
            },
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status.HTTP_403_FORBIDDEN,
            initial_detail={
                'message': 'Please provide a valid refresh token',
                'resolution': 'Please get an refresh token',
                'error_code': 'refresh_token_required',
            },
        )
    )

    @app.exception_handler(500)
    async def internal_server_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content={
                'message': 'Oops! Something went wrong',
                'error_code': 'server_error',
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
