from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.scene_audio_cache import SceneAudioCache
from app.repository.scene_audio_cache_repository import SceneAudioCacheRepository
from app.repository.story_repository import StoryRepository
from app.repository.voice_profile_repository import VoiceProfileRepository


class TTSService:
    def __init__(self, db: Session):
        self.story_repository = StoryRepository(db)
        self.voice_profile_repository = VoiceProfileRepository(db)
        self.scene_audio_cache_repository = SceneAudioCacheRepository(db)

    def request_scene_tts(
        self,
        *,
        story_scene_id: int,
        voice_profile_id: int,
    ) -> tuple[SceneAudioCache, str]:
        scene = self.story_repository.get_scene(story_scene_id)
        if scene is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story scene not found",
            )

        voice_profile = self.voice_profile_repository.get(voice_profile_id)
        if voice_profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice profile not found",
            )

        cache = self.scene_audio_cache_repository.get_by_scene_and_voice(
            story_scene_id=story_scene_id,
            voice_profile_id=voice_profile_id,
        )
        if cache is None:
            cache = self.scene_audio_cache_repository.create_pending(
                story_scene_id=story_scene_id,
                voice_profile_id=voice_profile_id,
            )

        return cache, scene.text

    def save_generated_audio_url(
        self,
        *,
        cache_id: int,
        audio_url: str,
        audio_object_key: str | None = None,
    ) -> SceneAudioCache:
        cache = self.scene_audio_cache_repository.get(cache_id)
        if cache is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scene audio cache not found",
            )
        return self.scene_audio_cache_repository.save_audio_url(
            cache,
            audio_url=audio_url,
            audio_object_key=audio_object_key,
        )

