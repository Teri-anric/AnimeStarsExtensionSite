import secrets

from ...database.repos import VerificationCodeRepository
from ...config import settings
from ..repos.pm import AnimestarPMRepo
from ..repos.auth import AnimestarAuthRepo
from ..exception import PMError


class VerificationService:
    def __init__(self):
        self.verification_code_repo = VerificationCodeRepository()

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
        code = self._generate_code()
        await self.verification_code_repo.create(username=username, code=code)

        # Send PM with the code
        message = (
            f"Your code: {code}\n"
            f"It code expired {settings.auth.code_expire_minutes} minutes."
        )
        await self._send_pm_message(username, message)

        return code

    async def verify_code(self, username: str, code: str) -> bool:
        """Verify the provided code for the username."""
        # Get valid verification code
        return await self.verification_code_repo.verify_code(
            username=username, code=code
        )

    async def mark_code_as_used(self, username: str, code: str) -> bool:
        """Mark the code as used."""
        is_valid = await self.verification_code_repo.verify_code(
            username=username, code=code
        )
        if not is_valid:
            return False
    
        return await self.verification_code_repo.mark_code_as_used(
            username=username, code=code
        )