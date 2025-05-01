class AnimestarError(Exception):
    pass


class RateLimitError(AnimestarError):
    INFO_MESSAGE = (
        "Вы достигли максимального количества неудачных попыток авторизации на сайте."
    )
    pass

class LoginError(AnimestarError):
    pass
