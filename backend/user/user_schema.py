from pydantic import BaseModel, EmailStr

from common.common_schema import Timestamped


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserRead(Timestamped):
    id: int
    email: EmailStr
    name: str
