class BaseEggsauceException(Exception):
    pass


class MultipleMembersFoundError(BaseEggsauceException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
