import secrets
import asyncio
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ...database.models import VerificationCode
from ...config import settings
from ..repos.pm import AnimestarPMRepo
from ..repos.auth import AnimestarAuthRepo
from ..exception import PMError


class VerificationService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    def _generate_code(self) -> str:
        """Generate a 6-digit verification code."""
        return str(secrets.randbelow(1000000)).zfill(6)

    async def _send_pm_message(self, username: str, message: str):
        """Send PM message with automatic re-login on failure."""
        try:
            repo = AnimestarPMRepo(settings.pm.cookie_file)
            result = await repo.send_pm(username, message)
            return result
        except PMError:
            print("Login failed, trying to login again")
            async with AnimestarAuthRepo(settings.pm.cookie_file) as auth_repo:
                await auth_repo.login(settings.pm.login, settings.pm.password)
            # Retry sending the message
            repo = AnimestarPMRepo(settings.pm.cookie_file)
            return await repo.send_pm(username, message)

    async def create_and_send_code(self, username: str) -> str:
        """Create a verification code and send it via PM."""
        # Deactivate any existing codes for this username
        await self.db_session.execute(
            update(VerificationCode)
            .where(VerificationCode.username == username)
            .values(is_active=False)
        )

        # Generate new code
        code = self._generate_code()
        
        # Create verification code record
        verification_code = VerificationCode(
            username=username,
            code=code,
        )
        self.db_session.add(verification_code)
        await self.db_session.commit()

        # Send PM with the code
        message = f"Ваш код верифікації: {code}\nКод дійсний протягом {settings.pm.code_expire_hours} години."
        await self._send_pm_message(username, message)

        return code

    async def verify_code(self, username: str, code: str) -> bool:
        """Verify the provided code for the username."""
        # Find the verification code
        stmt = select(VerificationCode).where(
            VerificationCode.username == username,
            VerificationCode.code == code,
            VerificationCode.is_active == True
        )
        result = await self.db_session.execute(stmt)
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            return False

        if not verification_code.is_valid:
            return False

        # Mark code as used
        verification_code.is_used = True
        await self.db_session.commit()

        return True

    async def cleanup_expired_codes(self):
        """Clean up expired verification codes."""
        stmt = update(VerificationCode).where(
            VerificationCode.expire_at < datetime.now(UTC).replace(tzinfo=None)
        ).values(is_active=False)
        
        await self.db_session.execute(stmt)
        await self.db_session.commit()