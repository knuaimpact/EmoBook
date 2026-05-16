from dataclasses import dataclass

import httpx


class ElevenLabsConfigurationError(RuntimeError):
    pass


class ElevenLabsAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class ElevenLabsVoice:
    voice_id: str
    requires_verification: bool = False


class ElevenLabsClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        tts_model_id: str,
        output_format: str,
        remove_background_noise: bool,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.tts_model_id = tts_model_id
        self.output_format = output_format
        self.remove_background_noise = remove_background_noise

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ElevenLabsConfigurationError(
                "EMOBOOK_ELEVENLABS_API_KEY is not configured"
            )
        return {"xi-api-key": self.api_key}

    async def create_voice(
        self,
        *,
        name: str,
        audio: bytes,
        filename: str,
        content_type: str | None,
    ) -> ElevenLabsVoice:
        files = {
            "files[]": (
                filename,
                audio,
                content_type or "application/octet-stream",
            )
        }
        data = {
            "name": name,
            "remove_background_noise": str(self.remove_background_noise).lower(),
            "description": "Parent voice profile for interactive bedtime story narration.",
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/v1/voices/add",
                headers=self._headers(),
                data=data,
                files=files,
            )
        if response.is_error:
            raise ElevenLabsAPIError(response.text)
        payload = response.json()
        return ElevenLabsVoice(
            voice_id=payload["voice_id"],
            requires_verification=payload.get("requires_verification", False),
        )

    async def create_speech(self, *, voice_id: str, text: str) -> bytes:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{self.base_url}/v1/text-to-speech/{voice_id}",
                headers={**self._headers(), "Content-Type": "application/json"},
                params={"output_format": self.output_format},
                json={
                    "text": text,
                    "model_id": self.tts_model_id,
                },
            )
        if response.is_error:
            raise ElevenLabsAPIError(response.text)
        return response.content
