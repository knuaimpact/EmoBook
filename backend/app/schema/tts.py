from pydantic import BaseModel

from app.model.scene_audio_cache import SceneAudioStatus
from app.schema.common import Timestamped


class TTSSceneRequestCreate(BaseModel):
    story_scene_id: int
    voice_profile_id: int


class AudioUrlSaveRequest(BaseModel):
    audio_url: str
    audio_object_key: str | None = None


class SceneAudioCacheRead(Timestamped):
    id: int
    story_scene_id: int
    voice_profile_id: int
    status: SceneAudioStatus
    audio_url: str | None = None
    audio_object_key: str | None = None
    error_message: str | None = None


class TTSSceneRequestRead(SceneAudioCacheRead):
    scene_text: str
