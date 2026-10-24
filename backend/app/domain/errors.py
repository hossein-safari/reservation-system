class DomainError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 409) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def not_found() -> DomainError:
    return DomainError("not_found", "The requested record was not found.", 404)
