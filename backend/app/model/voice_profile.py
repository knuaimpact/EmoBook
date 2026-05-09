from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.model.mixins import TimestampMixin


class VoiceProfile(TimestampMixin, Base):
    __tablename__ = "voice_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_audio_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    sample_audio_object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    provider_voice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user = relationship("User", back_populates="voice_profiles")
    scene_audio_caches = relationship("SceneAudioCache", back_populates="voice_profile")

