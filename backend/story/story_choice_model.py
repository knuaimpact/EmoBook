from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class StoryChoice(TimestampMixin, Base):
    __tablename__ = "story_choices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )
    choice_text: Mapped[str] = mapped_column(String(255), nullable=False)
    next_scene_id: Mapped[int | None] = mapped_column(
        ForeignKey("story_scenes.id"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="go_to_scene"
    )

    scene = relationship(
        "StoryScene", foreign_keys=[scene_id], back_populates="choices"
    )
    next_scene = relationship("StoryScene", foreign_keys=[next_scene_id])
