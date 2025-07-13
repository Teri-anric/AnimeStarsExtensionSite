from ..models import VerificationCode
from .crud import CRUDRepository

from sqlalchemy import select, and_


class VerificationCodeRepository(CRUDRepository):
    @property
    def entry_class(self) -> type[VerificationCode]:
        return VerificationCode

    async def verify_code(self, username: str, code: str) -> bool:
        code = await self.scalar(select(VerificationCode).where(
            and_(
                VerificationCode.username == username,
                VerificationCode.code == code,
            )
        ))

        if not code:
            return False
        
        await self.update(code.id, is_used=True)
        return True
