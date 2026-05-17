from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from voice.scene_audio_cache_model import SceneAudioCache
from voice.scene_audio_cache_repository import SceneAudioCacheRepository
from story.story_repository import StoryRepository
from voice.voice_profile_repository import VoiceProfileRepository
from storage import StorageService
from voice import ElevenLabsAPIError, ElevenLabsClient, ElevenLabsConfigurationError


class TTSService:
    def __init__(
        self,
        db: Session,
        storage_service: StorageService | None = None,
        elevenlabs_client: ElevenLabsClient | None = None,
    ):
        self.story_repository = StoryRepository(db)
        self.voice_profile_repository = VoiceProfileRepository(db)
        self.scene_audio_cache_repository = SceneAudioCacheRepository(db)
        self.storage_service = storage_service
        self.elevenlabs_client = elevenlabs_client

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

    async def generate_scene_audio(
        self,
        *,
        story_scene_id: int,
        voice_profile_id: int,
    ) -> SceneAudioCache:
        if self.storage_service is None or self.elevenlabs_client is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TTS dependencies are not configured",
            )

        cache, scene_text = self.request_scene_tts(
            story_scene_id=story_scene_id,
            voice_profile_id=voice_profile_id,
        )
        if cache.audio_url:
            return cache

        voice_profile = self.voice_profile_repository.get(voice_profile_id)
        if voice_profile is None or not voice_profile.provider_voice_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Voice profile is not ready for TTS",
            )

        self.scene_audio_cache_repository.mark_processing(cache)
        try:
            audio = await self.elevenlabs_client.create_speech(
                voice_id=voice_profile.provider_voice_id,
                text=scene_text,
            )
            stored = await self.storage_service.save_bytes(
                content=audio,
                folder=f"audio/{voice_profile_id}/{story_scene_id}",
                filename="scene.mp3",
            )
        except ElevenLabsConfigurationError as exc:
            self.scene_audio_cache_repository.mark_failed(cache, error_message=str(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        except ElevenLabsAPIError as exc:
            self.scene_audio_cache_repository.mark_failed(cache, error_message=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="ElevenLabs TTS request failed",
            ) from exc

        return self.scene_audio_cache_repository.save_audio_url(
            cache,
            audio_url=stored.url,
            audio_object_key=stored.object_key,
        )
