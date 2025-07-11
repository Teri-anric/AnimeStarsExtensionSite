from datetime import datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
from uuid import UUID

from ...config import settings
from ..schema.auth import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.auth.secret_key
ALGORITHM = settings.auth.algorithm


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expire: datetime | None = None) -> str:
    to_encode = data.copy()
    if expire:
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_id: str = payload.get("sub")
        user_id: str = payload.get("userid")
        if token_id is None or user_id is None:
            return None
        return TokenData(token_id=UUID(token_id), user_id=UUID(user_id))
    except JWTError:
        return None
