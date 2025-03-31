import aioredis

from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = aioredis.from_url(Config.REDIS_URL)


async def add_jit_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value='', ex=JTI_EXPIRY)


async def is_jit_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    return jti is not None
