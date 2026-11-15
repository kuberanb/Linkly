

from uuid import UUID

from pydantic import BaseModel,ConfigDict,HttpUrl

class URLCreate(BaseModel):
    original_url: HttpUrl


class URLResponse(BaseModel):
    id:UUID
    original_url: str
    short_code: str

    model_config = ConfigDict(from_attributes=True)
