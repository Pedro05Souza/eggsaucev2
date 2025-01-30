class BaseEggsauceException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class NoUpdateRequiredException(BaseEggsauceException):
    def __init__(self):
        super().__init__("The entity does not require an update.")


class NotInCacheException(BaseEggsauceException):
    def __init__(self):
        super().__init__("The entity is not in the cache.")
