from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.model.mixins import TimestampMixin


class ChildProfile(TimestampMixin, Base):
    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    preferred_style: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user = relationship("User", back_populates="child_profiles")
    sessions = relationship(
        "UserStorySession", back_populates="child_profile", cascade="all, delete-orphan"
    )
