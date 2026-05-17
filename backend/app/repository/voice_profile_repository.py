from sqlalchemy.orm import Session

from app.model.voice_profile import VoiceProfile, VoiceProfileStatus


class VoiceProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, voice_profile_id: int) -> VoiceProfile | None:
        return self.db.get(VoiceProfile, voice_profile_id)

    def create(
        self,
        *,
        user_id: int,
        name: str,
        sample_audio_url: str,
        sample_audio_object_key: str,
    ) -> VoiceProfile:
        voice_profile = VoiceProfile(
            user_id=user_id,
            name=name,
            sample_audio_url=sample_audio_url,
            sample_audio_object_key=sample_audio_object_key,
        )
        self.db.add(voice_profile)
        self.db.commit()
        self.db.refresh(voice_profile)
        return voice_profile

    def mark_ready(
        self, voice_profile: VoiceProfile, *, provider_voice_id: str
    ) -> VoiceProfile:
        voice_profile.provider = "elevenlabs"
        voice_profile.provider_voice_id = provider_voice_id
        voice_profile.status = VoiceProfileStatus.ready
        voice_profile.error_message = None
        self.db.commit()
        self.db.refresh(voice_profile)
        return voice_profile

    def mark_failed(
        self, voice_profile: VoiceProfile, *, error_message: str
    ) -> VoiceProfile:
        voice_profile.status = VoiceProfileStatus.failed
        voice_profile.error_message = error_message[:2000]
        self.db.commit()
        self.db.refresh(voice_profile)
        return voice_profile
