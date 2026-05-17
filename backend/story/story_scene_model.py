from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class StoryScene(TimestampMixin, Base):
    __tablename__ = "story_scenes"
    __table_args__ = (
        UniqueConstraint("story_id", "scene_order", name="uq_story_scenes_story_order"),
        UniqueConstraint("story_id", "scene_key", name="uq_story_scenes_scene_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id"), index=True, nullable=False
    )
    parent_scene_id: Mapped[int | None] = mapped_column(
        ForeignKey("story_scenes.id"), nullable=True
    )
    scene_key: Mapped[str] = mapped_column(String(100), nullable=False)
    scene_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    next_scene_id: Mapped[int | None] = mapped_column(
        ForeignKey("story_scenes.id"), nullable=True
    )
    is_ending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    emotion_tag: Mapped[str] = mapped_column(String(50), default="calm", nullable=False)
    generation_type: Mapped[str] = mapped_column(
        String(50), default="static", nullable=False
    )

    story = relationship("Story", back_populates="scenes")
    audio_caches = relationship("SceneAudioCache", back_populates="scene")
    choices = relationship(
        "StoryChoice",
        foreign_keys="[StoryChoice.scene_id]",
        back_populates="scene",
        cascade="all, delete-orphan",
    )
