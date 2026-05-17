from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from voice.voice_profile_model import VoiceProfile
from user.user_repository import UserRepository
from voice.voice_profile_repository import VoiceProfileRepository
from storage import StorageService
from voice import ElevenLabsAPIError, ElevenLabsClient, ElevenLabsConfigurationError


class VoiceProfileService:
    def __init__(
        self,
        db: Session,
        storage_service: StorageService,
        elevenlabs_client: ElevenLabsClient,
    ):
        self.user_repository = UserRepository(db)
        self.voice_profile_repository = VoiceProfileRepository(db)
        self.storage_service = storage_service
        self.elevenlabs_client = elevenlabs_client

    async def upload_parent_voice(
        self,
        *,
        user_id: int,
        profile_name: str,
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
        voice_profile = self.voice_profile_repository.create(
            user_id=user_id,
            name=profile_name,
            sample_audio_url=stored.url,
            sample_audio_object_key=stored.object_key,
        )

        try:
            await file.seek(0)
            audio = await file.read()
            elevenlabs_voice = await self.elevenlabs_client.create_voice(
                name=profile_name,
                audio=audio,
                filename=file.filename or "voice-sample.wav",
                content_type=file.content_type,
            )
        except (ElevenLabsAPIError, ElevenLabsConfigurationError) as exc:
            return self.voice_profile_repository.mark_failed(
                voice_profile,
                error_message=str(exc),
            )

        return self.voice_profile_repository.mark_ready(
            voice_profile,
            provider_voice_id=elevenlabs_voice.voice_id,
        )
