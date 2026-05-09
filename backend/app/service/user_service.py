from sqlalchemy.orm import Session

from app.model.user import User
from app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def create_user(self, *, email: str, name: str) -> User:
        return self.user_repository.create(email=email, name=name)

