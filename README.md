# EmoBook

## Backend MVP

FastAPI + SQLAlchemy + MySQL 기반 MVP API는 `backend/`에 있습니다.

### 실행

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
python seed.py
uvicorn app.main:app --reload
```

API 문서: `http://localhost:8000/docs`

### 주요 API

- `POST /api/v1/users`
- `GET /api/v1/stories`
- `GET /api/v1/stories/{story_id}`
- `GET /api/v1/stories/{story_id}/scenes`
- `GET /api/v1/stories/{story_id}/scenes/{scene_id}`
- `POST /api/v1/voice-profiles`
- `POST /api/v1/tts/scene-requests`
- `POST /api/v1/tts/scene-audio-caches/{cache_id}/audio-url`

초기 파일 저장은 `backend/local_storage`를 쓰며, `StorageService` 인터페이스 뒤에 구현을 분리해 두었습니다. GCS 전환 시 `app/storage`에 GCS 구현을 추가하고 `get_storage_service` 의존성만 교체하면 됩니다.
