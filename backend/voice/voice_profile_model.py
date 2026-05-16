import enum

from sqlalchemy import Enum, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database import Base
from common.mixins import TimestampMixin


class VoiceProfileStatus(str, enum.Enum):
    processing = "processing"
    ready = "ready"
    failed = "failed"


class VoiceProfile(TimestampMixin, Base):
    __tablename__ = "voice_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_audio_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    sample_audio_object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(50),
        default="elevenlabs",
        server_default="elevenlabs",
        nullable=False,
    )
    provider_voice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[VoiceProfileStatus] = mapped_column(
        Enum(VoiceProfileStatus),
        default=VoiceProfileStatus.processing,
        server_default=VoiceProfileStatus.processing.value,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="voice_profiles")
    scene_audio_caches = relationship("SceneAudioCache", back_populates="voice_profile")
