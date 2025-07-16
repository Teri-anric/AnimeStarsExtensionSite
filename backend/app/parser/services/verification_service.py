import secrets

from ..repos.pm import AnimestarPMRepo
from ..repos.auth import AnimestarAuthRepo
from ..exception import AnimestarError, UnauthorizedError

from ...database.repos.verification_code import VerificationCodeRepository
from ...config import settings
from ...database.repos.animestars_user import AnimestarsUserRepo
from ...database.models.animestars.user import AnimestarsUser


class VerificationServiceError(Exception):
    pass


class VerificationService:
    def __init__(self):
        self.verification_code_repo = VerificationCodeRepository()
        self.animestars_user = AnimestarsUserRepo()

    def _generate_code(self) -> str:
        """Generate a 6-digit verification code."""
        return str(secrets.randbelow(1000000)).zfill(6)

    def _generate_message(self, code: str) -> str:
        return (
            f"<p>Your code: {code}</p>\n"
            f"<p>It code expired {settings.auth.code_expire_minutes} minutes.</p>"
        )

    async def _send_pm_message(self, username: str, message: str):
        """Send PM message with automatic re-login on failure."""
        repo = AnimestarPMRepo(settings.pm.cookie_file)
        result = await repo.send_pm(username, message)
        return result

    async def _check_username(self, username: str) -> str:
        async with AnimestarAuthRepo(settings.pm.cookie_file) as auth_repo:
            try:
                user = await auth_repo.get_user(username)
                return user.username
            except UnauthorizedError:
                if not settings.pm.login or not settings.pm.password:
                    raise VerificationServiceError(
                        "Login and password are not set in the config"
                    )
                await auth_repo.login(settings.pm.login, settings.pm.password)
                user = await auth_repo.get_user(username)
                return user.username

    async def _get_or_create_user(self, username: str) -> AnimestarsUser:
        ani_user = await self.animestars_user.get_by_username(username)
        if not ani_user:
            ani_user = await self.animestars_user.create(username=username)
        return ani_user

    async def create_and_send_code(self, username: str) -> bool:
        """Create a verification code and send it via PM."""
        code_obj = await self.verification_code_repo.get_active_code(username=username)
        if code_obj:
            return True

        try:
            ani_user = await self._get_or_create_user(
                await self._check_username(username)
            )
        except AnimestarError:
            raise VerificationServiceError(f"Not found user {username}")

        code = self._generate_code()
        code_obj = await self.verification_code_repo.create(
            username=ani_user.username, code=code
        )

        try:
            await self._send_pm_message(username, self._generate_message(code))
        except Exception as e:
            await self.verification_code_repo.delete(code_obj.id)
            raise e
        return True

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
