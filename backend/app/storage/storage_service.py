from dataclasses import dataclass
from typing import Protocol

from fastapi import UploadFile


@dataclass(frozen=True)
class StoredObject:
    object_key: str
    url: str


class StorageService(Protocol):
    async def save_upload(self, *, file: UploadFile, folder: str) -> StoredObject:
        ...

