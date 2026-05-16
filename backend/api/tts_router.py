from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from voice.tts_schema import (
    AudioUrlSaveRequest,
    SceneAudioCacheRead,
    TTSSceneRequestCreate,
    TTSSceneRequestRead,
)
from common.dependencies import (
    get_database,
    get_elevenlabs_client,
    get_storage_service,
)
from voice.tts_service import TTSService
from storage import StorageService
from voice import ElevenLabsClient

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


@router.post(
    "/scene-audio-caches/{cache_id}/audio-url", response_model=SceneAudioCacheRead
)
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


@router.post("/generate", response_model=SceneAudioCacheRead)
async def generate_scene_audio(
    payload: TTSSceneRequestCreate,
    db: Session = Depends(get_database),
    storage_service: StorageService = Depends(get_storage_service),
    elevenlabs_client: ElevenLabsClient = Depends(get_elevenlabs_client),
) -> SceneAudioCacheRead:
    return await TTSService(
        db,
        storage_service,
        elevenlabs_client,
    ).generate_scene_audio(
        story_scene_id=payload.story_scene_id,
        voice_profile_id=payload.voice_profile_id,
    )
