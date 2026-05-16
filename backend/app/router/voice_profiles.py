from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.schema.voice_profile import VoiceProfileRead
from app.service.dependencies import (
    get_database,
    get_elevenlabs_client,
    get_storage_service,
)
from app.service.voice_profile_service import VoiceProfileService
from app.storage import StorageService
from app.voice import ElevenLabsClient

router = APIRouter(prefix="/voice-profiles", tags=["voice-profiles"])


@router.post("", response_model=VoiceProfileRead, status_code=201)
async def upload_parent_voice(
    user_id: int = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_database),
    storage_service: StorageService = Depends(get_storage_service),
    elevenlabs_client: ElevenLabsClient = Depends(get_elevenlabs_client),
) -> VoiceProfileRead:
    return await VoiceProfileService(
        db,
        storage_service,
        elevenlabs_client,
    ).upload_parent_voice(
        user_id=user_id,
        name=name,
        file=file,
    )
