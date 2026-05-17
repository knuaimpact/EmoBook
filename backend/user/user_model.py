from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), default="user", server_default="user", nullable=False
    )

    voice_profiles = relationship(
        "VoiceProfile",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    child_profiles = relationship(
        "ChildProfile",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    story_sessions = relationship(
        "UserStorySession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
