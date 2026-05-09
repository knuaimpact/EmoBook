from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.model.mixins import TimestampMixin


class StoryScene(TimestampMixin, Base):
    __tablename__ = "story_scenes"
    __table_args__ = (
        UniqueConstraint("story_id", "scene_order", name="uq_story_scenes_story_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), index=True, nullable=False)
    scene_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    story = relationship("Story", back_populates="scenes")
    audio_caches = relationship("SceneAudioCache", back_populates="scene")

