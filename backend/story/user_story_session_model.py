from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class UserStorySession(TimestampMixin, Base):
    __tablename__ = "user_story_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    child_profile_id: Mapped[int] = mapped_column(
        ForeignKey("child_profiles.id"), index=True, nullable=False
    )
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id"), index=True, nullable=False
    )
    current_scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )
    voice_profile_id: Mapped[int] = mapped_column(
        ForeignKey("voice_profiles.id"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active, completed, abandoned

    user = relationship("User", back_populates="story_sessions")
    child_profile = relationship("ChildProfile", back_populates="sessions")
    story = relationship("Story", back_populates="sessions")
    current_scene = relationship("StoryScene")
    voice_profile = relationship("VoiceProfile")
    choice_logs = relationship(
        "UserChoiceLog", back_populates="session", cascade="all, delete-orphan"
    )
