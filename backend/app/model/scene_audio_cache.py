import enum

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
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
            "story_scene_id",
            "voice_profile_id",
            name="uq_scene_audio_caches_scene_voice",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_scene_id: Mapped[int] = mapped_column(ForeignKey("story_scenes.id"), index=True, nullable=False)
    voice_profile_id: Mapped[int] = mapped_column(ForeignKey("voice_profiles.id"), index=True, nullable=False)
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

