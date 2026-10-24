class DomainError(Exception):
    """Business failure; transport status belongs to the presentation adapter."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)
