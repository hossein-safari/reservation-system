from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.errors.validation import ValidationError
from app.domain.validation import validate_name


@dataclass(eq=False)
class Resource:
    name: str
    description: str = ""
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = validate_name(self.name)
        self.description = self.description.strip()
        if len(self.description) > 2000:
            raise ValidationError(
                "invalid_description", "Description cannot exceed 2000 characters."
            )
