from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Self

import httpx
from http.cookiejar import LWPCookieJar
from bs4 import BeautifulSoup

from ..exception import AnimestarError, LoginHashError
from ..types import PaginatedBase
from ..utils import extract_login_hash

from app.config import settings


DEFAULT_BASE_URL = "https://animestars.org"
DEFAULT_PROXY = None


class AnimestarBaseRepo(AbstractAsyncContextManager):
    __COOKIES_CACHE = {}

    DEFAULT_HEADERS = {
        "user-agent": "TelegramBot (like @AnimeStarsBot)",
    }

    def __init__(self, cookie_file: Path | str | None = None, proxy: str | None = None, base_url: str | None = None) -> None:
        self.cookie_file = cookie_file
        self._client: httpx.AsyncClient | None = None
        self.base_url = base_url or settings.parser.base_url or DEFAULT_BASE_URL
        self.proxy = proxy or settings.parser.proxy or DEFAULT_PROXY
        self.users_hash: dict[str, str] = {}


    async def index(self) -> httpx.Response:
        return await self.client().get("/")

        
    async def get_user_hash(self, url: str = None) -> str:
        url = url or "/"
        if url not in self.users_hash:
            if login_hash := extract_login_hash(await self.get_page(url)):
                self.users_hash[url] = login_hash
            else:
                raise LoginHashError(url=url)
        return self.users_hash[url]


    async def get_page(self, url: str, **kwargs) -> BeautifulSoup:
        try:
            resp = await self.client().get(url, **kwargs)
            resp.raise_for_status()  # Raise an exception for 4XX/5XX responses
            return BeautifulSoup(await resp.aread(), "html.parser")
        except httpx.HTTPStatusError as e:
            raise AnimestarError(f"HTTP error {e.response.status_code} for {url}: {e.response.text}")
        except httpx.RequestError as e:
            raise AnimestarError(f"Request error for {url}: {e}")
        except Exception as e:
            raise AnimestarError(f"Failed to get page {url}: {e}")

    async def get_ajax_controller(
        self, mod: str, params: dict | None, is_html: bool = False
    ) -> dict | BeautifulSoup | None:
        resp = await self.client().get(
            "/engine/ajax/controller.php", params=dict(params or {}, mod=mod)
        )
        if is_html:
            return BeautifulSoup(await resp.aread(), "html.parser")
        if resp.content == b"":
            return None
        return resp.json()

    async def post_ajax_controller(
        self, mod: str, data: dict | str | None, is_html: bool = False
    ) -> dict | BeautifulSoup | None:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        resp = await self.client().post(
            "/engine/ajax/controller.php",
            params=dict(mod=mod),
            data=data,
            headers=headers,
        )
        if is_html:
            return BeautifulSoup(await resp.aread(), "html.parser")
        if resp.content == b"":
            return None
        return resp.json()
    
    def parse_pagination(self, soup: BeautifulSoup, cls: type[PaginatedBase], total: int, **kwargs) -> PaginatedBase:
        CURRENT_PAGE_SELECTOR = ".pagination__pages > span:not(.nav_ext)"
        PAGES_SELECTOR = ".pagination__pages > span, .pagination__pages > a"

        current_page = 1
        if _current_page_selector := soup.select_one(CURRENT_PAGE_SELECTOR):
            current_page = _current_page_selector.text.strip()

        last_page = 1
        if _last_page_selector := soup.select(PAGES_SELECTOR):
            last_page = _last_page_selector[-1].text.strip()
    
        return cls(
            current_page=current_page,
            last_page=last_page,
            total=total,
            **kwargs
        )

    def _get_cookie(self):
        _cookie = LWPCookieJar()
        if not self.cookie_file:
            return _cookie

        if self.cookie_file not in self.__COOKIES_CACHE:
            if Path(self.cookie_file).exists():
                try:
                    _cookie.load(self.cookie_file)
                except Exception as e:
                    raise AnimestarError(f"Failed to load cookie file {self.cookie_file}: {e}")

        return self.__COOKIES_CACHE.setdefault(self.cookie_file, _cookie)

    def _save_cookie(self):
        self._get_cookie().save(self.cookie_file)

    def client(self) -> httpx.AsyncClient:
        if not self._client or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.DEFAULT_HEADERS,
                cookies=self._get_cookie(),
                proxy=self.proxy,
                verify=False,
                http1=True,
                http2=True,
                follow_redirects=True,
                timeout=30.0
            )
        return self._client

    async def __aenter__(self) -> Self:
        """Return `self` upon entering the runtime context."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def close(self) -> None:
        if self.cookie_file:
            self._save_cookie()
        if self._client:
            await self._client.aclose()
