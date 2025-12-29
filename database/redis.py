from redis.asyncio import Redis
from config import env_config

token_blocklist = Redis(
    host=env_config.REDIS_HOST,
    port=env_config.REDIS_PORT,
    password=env_config.REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

async def add_jti_to_blocklist(jti: str) -> None:
    """Add a token's JTI to the blocklist in Redis."""
    await token_blocklist.set(
        name=jti,
        value="",
        ex=env_config.JTI_EXPIRY_SECONDS 
    )

async def is_jti_in_blocklist(jti: str) -> bool:
    """Check if a token's JTI is in the blocklist in Redis."""
    jti_exsist = await token_blocklist.exists(jti) 
    return jti_exsist == 1
