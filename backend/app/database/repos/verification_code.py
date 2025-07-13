from ..models import VerificationCode
from .crud import CRUDRepository

from sqlalchemy import select, and_


class VerificationCodeRepository(CRUDRepository):
    @property
    def entry_class(self) -> type[VerificationCode]:
        return VerificationCode

    async def get_active_code(self, username: str) -> VerificationCode | None:
        return await self.scalar(
            select(VerificationCode)
            .where(
                and_(
                    VerificationCode.username == username,
                    VerificationCode.is_used.is_(False),
                    VerificationCode.is_valid_sql.is_(True),
                )
            )
            .order_by(VerificationCode.created_at.desc())
            .limit(1)
        )

    async def get_code(self, username: str, code: str) -> VerificationCode | None:
        return await self.scalar(
            select(VerificationCode).where(
                and_(
                    VerificationCode.username == username,
                    VerificationCode.code == code,
                )
            )
        )

    async def verify_code(self, username: str, code: str) -> bool:
        code = await self.get_code(username, code)
        if not code:
            return False
        return code.is_valid

    async def mark_code_as_used(self, username: str, code: str) -> bool:
        code = await self.get_code(username, code)
        if not code:
            return False
        count = await self.update(code.id, is_used=True)
        return count > 0
