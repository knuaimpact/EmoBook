import enum

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.model.mixins import TimestampMixin


class SceneAudioStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class SceneAudioCache(TimestampMixin, Base):
    __tablename__ = "scene_audio_caches"
    __table_args__ = (
        UniqueConstraint(
            "voice_profile_id",
            "story_scene_id",
            "text_hash",
            "emotion_tag",
            "voice_settings_hash",
            "model_id",
            "output_format",
            name="uq_scene_audio_caches_full_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id"), index=True, nullable=False
    )
    story_scene_id: Mapped[int] = mapped_column(
        ForeignKey("story_scenes.id"), index=True, nullable=False
    )
    voice_profile_id: Mapped[int] = mapped_column(
        ForeignKey("voice_profiles.id"), index=True, nullable=False
    )

    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    emotion_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    voice_settings_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    output_format: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider: Mapped[str] = mapped_column(
        String(50), default="elevenlabs", nullable=False
    )

    status: Mapped[SceneAudioStatus] = mapped_column(
        Enum(SceneAudioStatus),
        default=SceneAudioStatus.pending,
        nullable=False,
    )
    audio_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    audio_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    scene = relationship("StoryScene", back_populates="audio_caches")
    voice_profile = relationship("VoiceProfile", back_populates="scene_audio_caches")
