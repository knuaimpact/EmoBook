from pydantic import BaseModel
from common.common_schema import Timestamped


class ChildProfileCreate(BaseModel):
    name: str
    age: int
    preferred_style: str | None = None


class ChildProfileRead(Timestamped):
    id: int
    user_id: int
    name: str
    age: int
    preferred_style: str | None = None
