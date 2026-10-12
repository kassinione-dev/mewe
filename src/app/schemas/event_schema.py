from datetime import UTC
from typing import Annotated

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

from ..field_limits import (
    EVENT_DESCRIPTION_MAX_LENGTH,
    EVENT_LOCATION_MAX_LENGTH,
    EVENT_MAX_DURATION_MINUTES,
    EVENT_MAX_PARTICIPANTS,
    EVENT_MIN_DURATION_MINUTES,
    EVENT_MIN_PARTICIPANTS,
    EVENT_TITLE_MAX_LENGTH,
)

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=EVENT_TITLE_MAX_LENGTH)
]
Location = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=EVENT_LOCATION_MAX_LENGTH)
]
Description = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=EVENT_DESCRIPTION_MAX_LENGTH)
]
# Клиент присылает дату с поясом (toISOString()); внутри всё храним в UTC
UTCDatetime = Annotated[AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]


class CreateEventRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: Title
    location: Location
    description: Description
    category_id: int = Field(alias="category", strict=True, gt=0)
    max_participants: int = Field(strict=True, ge=EVENT_MIN_PARTICIPANTS, le=EVENT_MAX_PARTICIPANTS)
    duration_minutes: int = Field(
        strict=True, ge=EVENT_MIN_DURATION_MINUTES, le=EVENT_MAX_DURATION_MINUTES
    )
    event_date: UTCDatetime
