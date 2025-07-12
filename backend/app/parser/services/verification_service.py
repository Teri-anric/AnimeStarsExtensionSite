import secrets
import asyncio
from datetime import datetime, UTC, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.repos import VerificationCodeRepository
from ...config import settings
from ..repos.pm import AnimestarPMRepo
from ..repos.auth import AnimestarAuthRepo
from ..exception import PMError


class VerificationService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = VerificationCodeRepository(db_session)

    def _generate_code(self) -> str:
        """Generate a 6-digit verification code."""
        return str(secrets.randbelow(1000000)).zfill(6)

    def _get_expire_at(self) -> datetime:
        """Get expiration time for the code."""
        return datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=settings.pm.code_expire_hours)

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
        await self.repo.deactivate_by_username(username)

        # Generate new code
        code = self._generate_code()
        expire_at = self._get_expire_at()
        
        # Create verification code record
        verification_code = await self.repo.create(username, code, expire_at)

        # Send PM with the code
        message = f"Ваш код верифікації: {code}\nКод дійсний протягом {settings.pm.code_expire_hours} години."
        await self._send_pm_message(username, message)

        return code

    async def verify_code(self, username: str, code: str) -> bool:
        """Verify the provided code for the username."""
        # Get valid verification code
        verification_code = await self.repo.get_valid_code(username, code)

        if not verification_code:
            return False

        # Mark code as used
        await self.repo.mark_as_used(str(verification_code.id))

        return True

    async def cleanup_expired_codes(self):
        """Clean up expired verification codes."""
        await self.repo.deactivate_expired_codes()

