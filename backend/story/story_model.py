from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class Story(TimestampMixin, Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    age_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    story_type: Mapped[str] = mapped_column(
        String(50), default="linear", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="draft", server_default="draft", nullable=False
    )

    scenes = relationship(
        "StoryScene",
        back_populates="story",
        cascade="all, delete-orphan",
        order_by="StoryScene.scene_order",
    )
    sessions = relationship(
        "UserStorySession",
        back_populates="story",
        cascade="all, delete-orphan",
    )
