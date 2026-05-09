from pydantic import BaseModel, EmailStr

from app.schema.common import Timestamped


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserRead(Timestamped):
    id: int
    email: EmailStr
    name: str
