from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Base, engine
from app.model import SceneAudioCache, Story, StoryScene, User, VoiceProfile
from app.router import stories, tts, users, voice_profiles

_models = (SceneAudioCache, Story, StoryScene, User, VoiceProfile)


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

app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(stories.router, prefix=settings.api_prefix)
app.include_router(voice_profiles.router, prefix=settings.api_prefix)
app.include_router(tts.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

