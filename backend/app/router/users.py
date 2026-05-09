from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schema.user import UserCreate, UserRead
from app.service.dependencies import get_database
from app.service.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_database),
) -> UserRead:
    return UserService(db).create_user(email=payload.email, name=payload.name)

