from app.schema.common import Timestamped


class VoiceProfileRead(Timestamped):
    id: int
    user_id: int
    name: str
    sample_audio_url: str
    sample_audio_object_key: str
    provider_voice_id: str | None = None

