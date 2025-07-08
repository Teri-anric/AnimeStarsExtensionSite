from sqlalchemy import select, func
from uuid import UUID, uuid4

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
    async def create_token(self, user_id: UUID) -> Token:
        db_token = Token(id=uuid4(), user_id=user_id)
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def deactivate_token(self, token_id: UUID) -> None:
        db_token = await self.get_token(token_id)
        if db_token:
            db_token.is_active = False
            await self.session.commit()
            await self.session.refresh(db_token) 

    @property
    def entry_class(self) -> type[Token]:
        return Token
