class BaseParserManagerError(Exception):
    message: str

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class NotImplementError(BaseParserManagerError):
    ...


class WorkerNotFoundError(BaseParserManagerError):
    ...
