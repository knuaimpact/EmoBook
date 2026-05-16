from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from common.config import get_settings
from common.database import Base, engine
from user.user_model import User
from user.child_profile_model import ChildProfile
from story.story_model import Story
from story.story_scene_model import StoryScene
from story.story_choice_model import StoryChoice
from story.user_story_session_model import UserStorySession
from story.user_choice_log_model import UserChoiceLog
from story.story_generation_job_model import StoryGenerationJob
from voice.voice_profile_model import VoiceProfile
from voice.scene_audio_cache_model import SceneAudioCache
from voice.tts_job_model import TTSJob

from api import (
    auth_router,
    child_profiles_router,
    sessions_router,
    stories_router,
    tts_router,
    users_router,
    voice_profiles_router,
)

_models = (
    User,
    ChildProfile,
    Story,
    StoryScene,
    StoryChoice,
    UserStorySession,
    UserChoiceLog,
    StoryGenerationJob,
    VoiceProfile,
    SceneAudioCache,
    TTSJob,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings.local_storage_root.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.public_storage_base_url,
    StaticFiles(directory=settings.local_storage_root),
    name="storage",
)

app.include_router(auth_router.router, prefix=settings.api_prefix)
app.include_router(child_profiles_router.router, prefix=settings.api_prefix)
app.include_router(users_router.router, prefix=settings.api_prefix)
app.include_router(stories_router.router, prefix=settings.api_prefix)
app.include_router(sessions_router.router, prefix=settings.api_prefix)
app.include_router(voice_profiles_router.router, prefix=settings.api_prefix)
app.include_router(tts_router.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
