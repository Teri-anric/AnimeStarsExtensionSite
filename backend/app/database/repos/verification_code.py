from datetime import datetime, UTC, timedelta
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import VerificationCode
from .base import BaseRepository


class VerificationCodeRepository(BaseRepository):
    def __init__(self, session: AsyncSession | None = None):
        if session:
            self.__session = session

    async def create(self, username: str, code: str, expire_at: datetime) -> VerificationCode:
        """Створити новий код верифікації."""
        verification_code = VerificationCode(
            username=username,
            code=code,
            expire_at=expire_at,
        )
        return await self.add(verification_code)

    async def get_by_username_and_code(self, username: str, code: str) -> VerificationCode | None:
        """Отримати код верифікації за username та code."""
        stmt = select(VerificationCode).where(
            and_(
                VerificationCode.username == username,
                VerificationCode.code == code,
                VerificationCode.is_active == True
            )
        )
        return await self.scalar(stmt)

    async def get_active_by_username(self, username: str) -> list[VerificationCode]:
        """Отримати всі активні коди для користувача."""
        stmt = select(VerificationCode).where(
            and_(
                VerificationCode.username == username,
                VerificationCode.is_active == True
            )
        )
        return await self.scalars(stmt)

    async def deactivate_by_username(self, username: str) -> None:
        """Деактивувати всі коди для користувача."""
        stmt = update(VerificationCode).where(
            VerificationCode.username == username
        ).values(is_active=False)
        await self.execute(stmt)

    async def mark_as_used(self, verification_code_id: str) -> None:
        """Позначити код як використаний."""
        stmt = update(VerificationCode).where(
            VerificationCode.id == verification_code_id
        ).values(is_used=True)
        await self.execute(stmt)

    async def deactivate_expired_codes(self) -> None:
        """Деактивувати застарілі коди."""
        stmt = update(VerificationCode).where(
            VerificationCode.expire_at < datetime.now(UTC).replace(tzinfo=None)
        ).values(is_active=False)
        await self.execute(stmt)

    async def delete_expired_codes(self) -> None:
        """Видалити застарілі коди."""
        stmt = select(VerificationCode).where(
            VerificationCode.expire_at < datetime.now(UTC).replace(tzinfo=None)
        )
        expired_codes = await self.scalars(stmt)
        
        if expired_codes:
            async with self.session as session:
                for code in expired_codes:
                    await session.delete(code)
                await session.commit()

    async def get_valid_code(self, username: str, code: str) -> VerificationCode | None:
        """Отримати валідний код верифікації."""
        verification_code = await self.get_by_username_and_code(username, code)
        
        if verification_code and verification_code.is_valid:
            return verification_code
        
        return None

    async def cleanup_old_codes(self, days_old: int = 7) -> None:
        """Очистити старі коди (старіше вказаної кількості днів)."""
        cutoff_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days_old)
        stmt = select(VerificationCode).where(
            VerificationCode.created_at < cutoff_date
        )
        old_codes = await self.scalars(stmt)
        
        if old_codes:
            async with self.session as session:
                for code in old_codes:
                    await session.delete(code)
                await session.commit()

    async def get_stats(self) -> dict:
        """Отримати статистику по кодам верифікації."""
        # Загальна кількість
        total_stmt = select(VerificationCode)
        total_codes = await self.scalars(total_stmt)
        
        # Активні коди
        active_stmt = select(VerificationCode).where(VerificationCode.is_active == True)
        active_codes = await self.scalars(active_stmt)
        
        # Використані коди
        used_stmt = select(VerificationCode).where(VerificationCode.is_used == True)
        used_codes = await self.scalars(used_stmt)
        
        # Застарілі коди
        expired_stmt = select(VerificationCode).where(
            VerificationCode.expire_at < datetime.now(UTC).replace(tzinfo=None)
        )
        expired_codes = await self.scalars(expired_stmt)
        
        return {
            "total": len(total_codes),
            "active": len(active_codes),
            "used": len(used_codes),
            "expired": len(expired_codes)
        }