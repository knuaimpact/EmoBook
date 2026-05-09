from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.scene_audio_cache import SceneAudioCache, SceneAudioStatus


class SceneAudioCacheRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, cache_id: int) -> SceneAudioCache | None:
        return self.db.get(SceneAudioCache, cache_id)

    def get_by_scene_and_voice(
        self,
        *,
        story_scene_id: int,
        voice_profile_id: int,
    ) -> SceneAudioCache | None:
        stmt = select(SceneAudioCache).where(
            SceneAudioCache.story_scene_id == story_scene_id,
            SceneAudioCache.voice_profile_id == voice_profile_id,
        )
        return self.db.scalar(stmt)

    def create_pending(
        self,
        *,
        story_scene_id: int,
        voice_profile_id: int,
    ) -> SceneAudioCache:
        cache = SceneAudioCache(
            story_scene_id=story_scene_id,
            voice_profile_id=voice_profile_id,
            status=SceneAudioStatus.pending,
        )
        self.db.add(cache)
        self.db.commit()
        self.db.refresh(cache)
        return cache

    def save_audio_url(
        self,
        cache: SceneAudioCache,
        *,
        audio_url: str,
        audio_object_key: str | None = None,
    ) -> SceneAudioCache:
        cache.audio_url = audio_url
        cache.audio_object_key = audio_object_key
        cache.status = SceneAudioStatus.completed
        cache.error_message = None
        self.db.commit()
        self.db.refresh(cache)
        return cache

