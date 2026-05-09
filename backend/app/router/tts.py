from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schema.tts import (
    AudioUrlSaveRequest,
    SceneAudioCacheRead,
    TTSSceneRequestCreate,
    TTSSceneRequestRead,
)
from app.service.dependencies import get_database
from app.service.tts_service import TTSService

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("/scene-requests", response_model=TTSSceneRequestRead, status_code=202)
def request_scene_tts(
    payload: TTSSceneRequestCreate,
    db: Session = Depends(get_database),
) -> TTSSceneRequestRead:
    cache, scene_text = TTSService(db).request_scene_tts(
        story_scene_id=payload.story_scene_id,
        voice_profile_id=payload.voice_profile_id,
    )
    cache_data = SceneAudioCacheRead.model_validate(cache).model_dump()
    return TTSSceneRequestRead(**cache_data, scene_text=scene_text)



@router.post("/scene-audio-caches/{cache_id}/audio-url", response_model=SceneAudioCacheRead)
def save_generated_audio_url(
    cache_id: int,
    payload: AudioUrlSaveRequest,
    db: Session = Depends(get_database),
) -> SceneAudioCacheRead:
    return TTSService(db).save_generated_audio_url(
        cache_id=cache_id,
        audio_url=payload.audio_url,
        audio_object_key=payload.audio_object_key,
    )
