from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.model.voice_profile import VoiceProfile
from app.repository.user_repository import UserRepository
from app.repository.voice_profile_repository import VoiceProfileRepository
from app.storage import StorageService


class VoiceProfileService:
    def __init__(self, db: Session, storage_service: StorageService):
        self.user_repository = UserRepository(db)
        self.voice_profile_repository = VoiceProfileRepository(db)
        self.storage_service = storage_service

    async def upload_parent_voice(
        self,
        *,
        user_id: int,
        name: str,
        file: UploadFile,
    ) -> VoiceProfile:
        user = self.user_repository.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if file.content_type and not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Voice sample must be an audio file",
            )

        stored = await self.storage_service.save_upload(
            file=file,
            folder=f"voice-profiles/{user_id}",
        )
        return self.voice_profile_repository.create(
            user_id=user_id,
            name=name,
            sample_audio_url=stored.url,
            sample_audio_object_key=stored.object_key,
        )

