from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from voice.voice_profile_schema import VoiceProfileRead
from common.dependencies import (
    get_database,
    get_elevenlabs_client,
    get_storage_service,
)
from voice.voice_profile_service import VoiceProfileService
from storage import StorageService
from voice import ElevenLabsClient

router = APIRouter(prefix="/voice-profiles", tags=["voice-profiles"])


@router.post("", response_model=VoiceProfileRead, status_code=201)
async def upload_parent_voice(
    user_id: int = Form(...),
    profile_name: str = Form(...),
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
        profile_name=profile_name,
        file=file,
    )
