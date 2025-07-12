class AnimestarError(Exception):
    pass


class RateLimitError(AnimestarError):
    INFO_MESSAGE = (
        "Вы достигли максимального количества неудачных попыток авторизации на сайте."
    )
    pass

class LoginError(AnimestarError):
    pass


class LoginHashError(AnimestarError):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Failed to get login hash for {url}")

class PMError(AnimestarError):
    pass