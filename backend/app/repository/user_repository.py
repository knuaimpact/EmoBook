from sqlalchemy.orm import Session

from app.model.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def create(self, *, email: str, name: str) -> User:
        user = User(email=email, name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

