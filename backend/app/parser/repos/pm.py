from .base import AnimestarBaseRepo

from ..exception import PMError
from ..utils import from_data


class AnimestarPMRepo(AnimestarBaseRepo):
    async def send_pm(self, username: str, message: str):
        """Send a PM to a user."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        resp = await self.client().post(
            "/engine/mods/pm/ajax.php",
            data=from_data({
                "message": message,
                "name": username,
                "action": "send",
            }),
            headers=headers,
        )
        try:
            return resp.json()
        except Exception as e:
            raise PMError(e)
