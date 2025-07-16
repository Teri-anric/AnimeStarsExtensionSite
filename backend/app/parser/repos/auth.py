from contextlib import suppress
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from ..exception import RateLimitError, LoginError, AnimestarError, UnauthorizedError
from ..utils import find_message_info, from_data
from ..types import AnimestarsUser
from .base import AnimestarBaseRepo


class AnimestarAuthRepo(AnimestarBaseRepo):
    LOGIN_TITLE_SELECTOR = ".lgn__name > span"

    def assert_login(self, soup: BeautifulSoup) -> str:
        username_elm = soup.select_one(self.LOGIN_TITLE_SELECTOR)
        if username_elm:
            return username_elm.text.strip()
        raise UnauthorizedError("Not found login title")

    async def login(self, username: str, password: str) -> str:
        """
        Login to Animestar.
        
        Returns the username of the logged in user.
        Raises LoginError if the login fails.
        """
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
            return self.assert_login(soup)
        raise LoginError(*find_message_info(page))

    async def get_user(self, username: str) -> AnimestarsUser:
        """Get a user by username."""
        USERNAME_SELECTOR = ".usn__name h1"
        CLUB_SELECTOR = ".usn__club-item-top a"

        soup = await self.get_page(f"/user/{quote_plus(username)}")
        self.assert_login(soup)

        username_elm = soup.select_one(USERNAME_SELECTOR)
        if not username_elm:
            raise AnimestarError("Not found username")
        username = username_elm.text.strip()

        club_elm = soup.select_one(CLUB_SELECTOR)
        club_id = None
        with suppress(Exception):
            club_url = club_elm["href"].strip("/")
            club_id = int(club_url.split("/")[-1])

        return AnimestarsUser(username=username, club_id=club_id)
