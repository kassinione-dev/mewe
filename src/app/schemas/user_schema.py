from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from ..field_limits import USER_ABOUT_MAX_LENGTH

About = Annotated[str, StringConstraints(strip_whitespace=True, max_length=USER_ABOUT_MAX_LENGTH)]


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    # Пустая строка — описание стёрли
    about: About = ""
