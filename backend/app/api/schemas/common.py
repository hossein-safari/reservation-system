from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.validation import MAX_AMOUNT_IRR

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Amount = Annotated[int, Field(gt=0, le=MAX_AMOUNT_IRR, strict=True)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Output(BaseModel):
    model_config = ConfigDict(from_attributes=True)
