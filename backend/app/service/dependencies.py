from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.storage import LocalStorageService, StorageService


def get_storage_service(settings: Settings = Depends(get_settings)) -> StorageService:
    return LocalStorageService(
        root=settings.local_storage_root,
        public_base_url=settings.public_storage_base_url,
    )


def get_database(db: Session = Depends(get_db)) -> Session:
    return db

