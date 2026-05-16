# EmoBook

아이들을 위한 인터랙티브 동화 낭독 백엔드입니다. MVP는 FastAPI, MySQL, 개발용 로컬 파일 저장소를 사용하고, 부모 목소리 복제와 장면 단위 TTS 생성은 ElevenLabs로 처리합니다.

## 포함된 기능

- 사용자 생성
- 동화 및 장면 조회
- 부모 음성 샘플 업로드
- ElevenLabs Instant Voice Cloning 연동: `POST /v1/voices/add`
- 장면 TTS 생성 연동: `POST /v1/text-to-speech/{voice_id}`
- MySQL 기반 오디오 캐시 메타데이터 저장
- 생성된 오디오 파일 `/storage` 경로로 제공

## 디렉터리 구조

```text
EmoBook/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                  # FastAPI 앱 진입점, 라우터 등록, 스토리지 마운트
│  │  ├─ config.py                # DB, 스토리지, ElevenLabs 환경설정
│  │  ├─ database.py              # SQLAlchemy 엔진, 세션, Base
│  │  ├─ model/                   # SQLAlchemy 데이터베이스 모델
│  │  ├─ schema/                  # Pydantic 요청/응답 스키마
│  │  ├─ repository/              # 데이터베이스 접근 계층
│  │  ├─ service/                 # 비즈니스 로직
│  │  ├─ router/                  # FastAPI 엔드포인트 정의
│  │  ├─ storage/                 # 저장소 추상화 및 로컬 저장 구현
│  │  └─ voice/                   # ElevenLabs API 클라이언트
│  ├─ migrations/
│  │  └─ 001_elevenlabs_voice_profiles.sql
│  ├─ local_storage/              # 개발용 업로드/생성 오디오 파일 저장소
│  ├─ docker-compose.yml          # 로컬 MySQL 실행 설정
│  ├─ requirements.txt            # Python 의존성
│  ├─ seed.py                     # 데모 사용자/동화/장면 시드 데이터
│  └─ .env.example                # 환경변수 예시 파일
├─ MeloTTS/                       # 기존 로컬 TTS 연구/참고 코드
├─ OpenVoice/                     # 기존 음성 복제 연구/참고 코드
└─ README.md
```

## 백엔드 흐름

음성 샘플 업로드:

```text
router/voice_profiles.py
-> service/voice_profile_service.py
-> storage/local_storage_service.py
-> voice/elevenlabs_client.py
-> repository/voice_profile_repository.py
-> model/voice_profile.py
```

장면 TTS 생성:

```text
router/tts.py
-> service/tts_service.py
-> repository/story_repository.py
-> repository/voice_profile_repository.py
-> voice/elevenlabs_client.py
-> storage/local_storage_service.py
-> repository/scene_audio_cache_repository.py
```

동화 조회:

```text
router/stories.py
-> service/story_service.py
-> repository/story_repository.py
-> model/story.py, model/story_scene.py
```

`backend/app/voice/`는 ElevenLabs 연동 경계입니다. 외부 provider 호출을 이 위치에 격리해두었기 때문에, 이후 Google TTS나 자체 TTS provider를 추가하더라도 핵심 동화 로직과 캐시 로직을 크게 바꾸지 않아도 됩니다.

## 로컬 실행

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`backend/.env`에 ElevenLabs API 키를 설정합니다.

```env
EMOBOOK_ELEVENLABS_API_KEY=your_key_here
```

MySQL과 API 서버를 실행합니다.

```powershell
docker compose up -d
python seed.py
uvicorn app.main:app --reload
```

API 문서: `http://localhost:8000/docs`

이미 이전 버전의 로컬 데이터베이스를 사용 중이라면, 업데이트된 voice profile API를 사용하기 전에 `backend/migrations/001_elevenlabs_voice_profiles.sql`을 적용하세요.

## 주요 API 사용 흐름

1. 사용자 생성: `POST /api/v1/users`
2. 부모 음성 샘플 업로드: `POST /api/v1/voice-profiles`
3. 동화 및 장면 조회: `GET /api/v1/stories`
4. 장면 낭독 오디오 생성: `POST /api/v1/tts/generate`
5. 응답으로 받은 `audio_url` 재생

## 환경변수

```env
EMOBOOK_DATABASE_URL=mysql+pymysql://emobook:emobook@localhost:3306/emobook
EMOBOOK_LOCAL_STORAGE_ROOT=backend/local_storage
EMOBOOK_PUBLIC_STORAGE_BASE_URL=/storage
EMOBOOK_ELEVENLABS_API_KEY=
EMOBOOK_ELEVENLABS_TTS_MODEL_ID=eleven_multilingual_v2
EMOBOOK_ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128
```

## 참고 사항

현재 코드는 백엔드 MVP 단계입니다. 기획 문서에는 아이 프로필, 세션, 선택지 기반 분기, LLM 장면 생성, Redis, Cloud Storage, Cloud Tasks가 포함되어 있습니다. 지금 구조는 storage와 ElevenLabs 경계를 분리해두었기 때문에 이후 기능을 단계적으로 추가하기 쉽게 되어 있습니다.
