from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.model.user import User
from app.schema.child_profile import ChildProfileCreate, ChildProfileRead
from app.service.child_profile_service import ChildProfileService
from app.service.dependencies import get_database, get_current_user

router = APIRouter(prefix="/child-profiles", tags=["child_profiles"])


@router.post("", response_model=ChildProfileRead, status_code=201)
def create_child_profile(
    payload: ChildProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
) -> ChildProfileRead:
    return ChildProfileService(db).create_profile(
        user_id=current_user.id, payload=payload
    )


@router.get("", response_model=list[ChildProfileRead])
def get_child_profiles(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_database)
) -> list[ChildProfileRead]:
    return ChildProfileService(db).get_profiles_by_user(user_id=current_user.id)
