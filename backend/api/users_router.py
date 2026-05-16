from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from user.user_schema import UserCreate, UserRead
from common.dependencies import get_database
from user.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_database),
) -> UserRead:
    return UserService(db).create_user(email=payload.email, name=payload.name)
