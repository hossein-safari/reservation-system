from app.domain.errors.base import DomainError


class NotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("not_found", "The requested record was not found.")
