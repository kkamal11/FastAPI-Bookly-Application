from passlib.context import CryptContext
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
import jwt
import uuid
import logging
from config import env_config


pwd_context = CryptContext(
    schemes=["bcrypt"]
)

def generate_password_hash(password: str) -> str:
    """Generate a hashed password."""
    hashed_password = pwd_context.hash(password)
    return hashed_password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_data: dict,expiry: timedelta = None, refresh:bool = False) -> str:
    """Create a JWT access token for the given user data."""
    payload = {}
    payload['user'] = user_data
    payload["exp"] = datetime.utcnow() + timedelta(
                minutes=expiry if expiry is not None else env_config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload = payload,
        key=env_config.JWT_SECRET_KEY,
        algorithm=env_config.JWT_ALGORITHM,
    )
    return token


def decode_access_token(token: str) -> dict | None:
    """Decode a JWT access token and return the payload."""
    try:
        token_data = jwt.decode(
            jwt=token.encode('utf-8'),
            key=env_config.JWT_SECRET_KEY,
            algorithms=[env_config.JWT_ALGORITHM],
        )

        return token_data
    except jwt.ExpiredSignatureError as e:
        logging.exception(e)
        return None
    except jwt.InvalidTokenError as e:
        logging.exception(e)
        return None
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


def create_url_safe_token(data: dict):
    """Create a URL-safe timed token for the given data."""
    serializer = URLSafeTimedSerializer(
        env_config.JWT_SECRET_KEY,
        salt="email-configuration-salt"
    )
    token = serializer.dumps(data, salt="email-configuration-salt")
    return token    

def decode_url_safe_token(token: str, max_age: int = 600):
    """Decode a URL-safe timed token and return the data."""
    serializer = URLSafeTimedSerializer(
        env_config.JWT_SECRET_KEY,
        salt="email-configuration-salt"
    )
    try:
        token_data = serializer.loads(
            token,
            salt="email-configuration-salt",
            max_age=max_age
        )
        return token_data
    except Exception as e:
        logging.exception(str(e))
        return None
