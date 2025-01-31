class BaseEggsauceException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class NoUpdateRequiredException(BaseEggsauceException):
    def __init__(self):
        super().__init__("This entity is already up-to-date. No update is required.")


class NotInCacheException(BaseEggsauceException):
    def __init__(self):
        super().__init__("The entity is supposed to be in the cache, but it's not.")
