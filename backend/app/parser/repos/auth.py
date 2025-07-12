from urllib.parse import quote

from bs4 import BeautifulSoup

from ..exception import RateLimitError, LoginError
from ..utils import find_message_info, from_data
from .base import AnimestarBaseRepo


class AnimestarAuthRepo(AnimestarBaseRepo):

    async def login(self, username: str, password: str) -> str:
        """
        Login to Animestar.
        
        Returns the username of the logged in user.
        Raises LoginError if the login fails.
        """
        LOGIN_TITLE_SELECTOR = ".lgn__name > span"
        data = from_data(
            {"login_name": username, "login_password": password, "login": "submit"}
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        resp = await self.client().post("/", data=data, headers=headers)
        page = await resp.aread()
        if RateLimitError.INFO_MESSAGE.encode() in page:
            raise RateLimitError(*find_message_info(page))
        if "Ошибка авторизации".encode() not in page:
            soup = BeautifulSoup(page, "html.parser")
            elm = soup.select_one(LOGIN_TITLE_SELECTOR)
            if elm:
                raise LoginError("Not found login title")
            return elm.text.strip()
        raise LoginError(*find_message_info(page))
