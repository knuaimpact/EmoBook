from sqlalchemy import select
from sqlalchemy.orm import Session
from app.model.child_profile import ChildProfile
from app.schema.child_profile import ChildProfileCreate, ChildProfileRead


class ChildProfileService:
    def __init__(self, db: Session):
        self.db = db

    def create_profile(
        self, user_id: int, payload: ChildProfileCreate
    ) -> ChildProfileRead:
        profile = ChildProfile(
            user_id=user_id,
            name=payload.name,
            age=payload.age,
            preferred_style=payload.preferred_style,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return ChildProfileRead.model_validate(profile)

    def get_profiles_by_user(self, user_id: int) -> list[ChildProfileRead]:
        profiles = self.db.scalars(
            select(ChildProfile).where(ChildProfile.user_id == user_id)
        ).all()
        return [ChildProfileRead.model_validate(p) for p in profiles]
