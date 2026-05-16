from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from common.config import Settings, get_settings
from common.database import get_db
from user.user_model import User
from storage import LocalStorageService, StorageService
from voice import ElevenLabsClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    return LocalStorageService(
        root=settings.local_storage_root,
        public_base_url=settings.public_storage_base_url,
    )


def get_database(db: Session = Depends(get_db)) -> Session:
    return db


def get_elevenlabs_client(
    settings: Settings = Depends(get_settings),
) -> ElevenLabsClient:
    return ElevenLabsClient(
        api_key=settings.elevenlabs_api_key,
        base_url=settings.elevenlabs_base_url,
        tts_model_id=settings.elevenlabs_tts_model_id,
        output_format=settings.elevenlabs_output_format,
        remove_background_noise=settings.elevenlabs_remove_background_noise,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_database),
    settings: Settings = Depends(get_settings),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
