from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from storage.storage_service import StoredObject


class LocalStorageService:
    def __init__(self, *, root: Path, public_base_url: str):
        self.root = root
        self.public_base_url = public_base_url.rstrip("/")

    async def save_upload(self, *, file: UploadFile, folder: str) -> StoredObject:
        extension = Path(file.filename or "").suffix.lower()
        object_key = f"{folder.strip('/')}/{uuid4().hex}{extension}"
        target_path = self.root / object_key
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)

        normalized_key = object_key.replace("\\", "/")
        return StoredObject(
            object_key=normalized_key,
            url=f"{self.public_base_url}/{normalized_key}",
        )

    async def save_bytes(
        self,
        *,
        content: bytes,
        folder: str,
        filename: str,
    ) -> StoredObject:
        safe_name = Path(filename).name
        object_key = f"{folder.strip('/')}/{uuid4().hex}-{safe_name}"
        target_path = self.root / object_key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

        normalized_key = object_key.replace("\\", "/")
        return StoredObject(
            object_key=normalized_key,
            url=f"{self.public_base_url}/{normalized_key}",
        )
