from fastapi import Depends, WebSocketException, status, Query
from typing import Annotated

from ...database.models.user import User, Token
from .deps import UserRepositoryDep, TokenRepositoryDep
from .utils import decode_token


async def ws_get_token_obj(
    token: str = Query(..., description="JWT token"),
    token_repo: TokenRepositoryDep = None,
) -> Token:
    credentials_exception = WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        detail="Could not validate credentials",
    )

    token_data = await decode_token(token)
    if token_data is None:
        raise credentials_exception

    token = await token_repo.get(token_data.token_id)
    if token is None or not token.is_active:
        raise credentials_exception

    return token


async def ws_get_current_user(
    token: Token = Depends(ws_get_token_obj),
    user_repo: UserRepositoryDep = None,
) -> User:
    if token.user_id is None:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            detail="User not found",
        )
    user = await user_repo.get(token.user_id)
    if user is None or not user.is_active:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            detail="User not found",
        )
    return user



WsProtectedDep = Depends(ws_get_current_user)
WsUserDep = Annotated[User, WsProtectedDep]
