import logging
import uuid
from datetime import datetime, timedelta

from itsdangerous import URLSafeTimedSerializer
import jwt
from passlib.context import CryptContext

from src.config import Config

passwd_context = CryptContext(
    schemes=['bcrypt'],
)


def generate_password_hash(password: str) -> str:
    return passwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return passwd_context.verify(plain_password, hashed_password)


def create_access_token(user_data: dict, expiry: timedelta=None, refresh: bool=False) -> str:
    payload = {
        'user': user_data,
        'exp': datetime.utcnow() + (expiry if expiry is not None else timedelta(minutes=60)),
        'jit': str(uuid.uuid4()),
        'refresh': refresh
    }

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_KEY,
        algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict|None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_KEY,
            algorithms=[Config.JWT_ALGORITHM],
        )
    except jwt.PyJWTError as jwt_ex:
        logging.exception(jwt_ex)
        return None
    except Exception as ex:
        logging.exception(ex)
        return None

    return token_data


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_KEY, salt='email-configuration'
)


def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token


def verify_url_safe_token(token: str, max_age: int=60) -> dict|None:
    try:
        token_data = serializer.loads(token, max_age=max_age)
        return token_data
    except Exception as ex:
        logging.error(str(ex))
