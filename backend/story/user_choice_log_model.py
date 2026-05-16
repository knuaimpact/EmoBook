from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class UserChoiceLog(TimestampMixin, Base):
    __tablename__ = "user_choice_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("user_story_sessions.id"), index=True, nullable=False
    )
    scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )
    choice_id: Mapped[int] = mapped_column(
        ForeignKey("story_choices.id"), index=True, nullable=False
    )

    session = relationship("UserStorySession", back_populates="choice_logs")
    scene = relationship("StoryScene")
    choice = relationship("StoryChoice")
