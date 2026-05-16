import enum
from sqlalchemy import Enum, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.model.mixins import TimestampMixin


class TTSJobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class TTSJob(TimestampMixin, Base):
    __tablename__ = "tts_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    voice_profile_id: Mapped[int] = mapped_column(
        ForeignKey("voice_profiles.id"), index=True, nullable=False
    )
    scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    emotion_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    voice_settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_format: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[TTSJobStatus] = mapped_column(
        Enum(TTSJobStatus), default=TTSJobStatus.pending, nullable=False
    )
    provider_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
