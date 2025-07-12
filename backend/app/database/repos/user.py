from datetime import datetime
from sqlalchemy import select, func
from uuid import UUID, uuid4
from typing import List

from ..models.user import User, Token
from .crud import CRUDRepository


class UserRepository(CRUDRepository[User, UUID]):
    async def create_user(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        return await self.scalar(select(User).where(func.lower(User.username) == username.lower()))

    @property
    def entry_class(self) -> type[User]:
        return User


class TokenRepository(CRUDRepository[Token, UUID]):
    async def deactivate_token(self, token_id: UUID) -> None:
        db_token = await self.get_token(token_id)
        if db_token:
            db_token.is_active = False
            await self.session.commit()
            await self.session.refresh(db_token)

    async def get_active_sessions_by_user_id(self, user_id: UUID) -> List[Token]:
        """Get all active sessions for a specific user"""
        stmt = select(Token).where(
            Token.user_id == user_id,
            Token.is_active == True
        ).order_by(Token.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_token(self, token_id: UUID) -> Token | None:
        """Get a specific token by ID"""
        return await self.get(token_id)

    @property
    def entry_class(self) -> type[Token]:
        return Token
