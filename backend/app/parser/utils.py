from urllib.parse import urlencode
from bs4 import BeautifulSoup


__all__ = ["clear_unset", "extract_login_hash", "from_data", "find_message_info"]


def find_message_info(page: str) -> list[str]:
    return [elm.text for elm in BeautifulSoup(page).css.select(".message-info")]


def from_data(data: dict) -> str:
    return urlencode(data, doseq=True, encoding="utf-8")


def clear_unset(params: dict):
    return {k: v for k, v in params.items() if v is not None}


def extract_login_hash(soup: BeautifulSoup) -> str | None:
    for x in soup.find_all("script"):
        if "var dle_login_hash = " in x.text:
            return x.text.split("var dle_login_hash = ")[1].split(";")[0].strip("'")
