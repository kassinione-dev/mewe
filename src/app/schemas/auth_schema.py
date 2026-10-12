from pydantic import BaseModel, ConfigDict, Field


class CreateSessionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    init_data: str = Field(alias="initData", min_length=1)
    # Только для диагностики отказов в логе
    platform: str = ""
    version: str = ""
