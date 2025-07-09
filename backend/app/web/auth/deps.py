from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from ...database.models.user import User, Token
from ...database.repos.user import UserRepository, TokenRepository
from .utils import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


TokenRepositoryDep = Annotated[TokenRepository, Depends(lambda: TokenRepository())]
UserRepositoryDep = Annotated[UserRepository, Depends(lambda: UserRepository())]


async def get_token_obj(
    token: str = Depends(oauth2_scheme),
    token_repo: TokenRepositoryDep = None,
) -> Token:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = await decode_token(token)
    if token_data is None:
        raise credentials_exception

    token = await token_repo.get(token_data.token_id)
    if token is None:
        raise credentials_exception

    return token


async def get_current_user(
    token: Token = Depends(get_token_obj),
    user_repo: UserRepositoryDep = None,
) -> User:
    if token.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    user = await user_repo.get(token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_optional_current_user(
    token: Token = Depends(get_token_obj),
    user_repo: UserRepositoryDep = None,
) -> User | None:
    if token.user_id is None:
        return None
    return await user_repo.get(token.user_id)


TokenDep = Annotated[Token, Depends(get_token_obj)]
UserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[User, Depends(get_optional_current_user)]
