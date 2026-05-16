import enum
from sqlalchemy import Enum, ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from common.database import Base
from common.mixins import TimestampMixin


class StoryGenerationJobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class StoryGenerationJob(TimestampMixin, Base):
    __tablename__ = "story_generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("user_story_sessions.id"), index=True, nullable=False
    )
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id"), index=True, nullable=False
    )
    source_scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )
    choice_id: Mapped[int] = mapped_column(
        ForeignKey("story_choices.id"), index=True, nullable=False
    )
    generated_scene_id: Mapped[int | None] = mapped_column(
        ForeignKey("story_scenes.id"), nullable=True
    )

    status: Mapped[StoryGenerationJobStatus] = mapped_column(
        Enum(StoryGenerationJobStatus),
        default=StoryGenerationJobStatus.pending,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
