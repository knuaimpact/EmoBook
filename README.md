# EmoBook

아이들을 위한 인터랙티브 동화 낭독 백엔드입니다. MVP는 FastAPI, PostgreSQL, 개발용 로컬 파일 저장소를 사용하고, 부모 목소리 복제와 장면 단위 TTS 생성은 ElevenLabs로 처리합니다.

## 포함된 기능

- 사용자 생성 및 JWT 인증
- 아이 프로필 관리
- 인터랙티브/리니어 동화 및 장면 조회
- 읽기 세션 저장 및 복원 (이어읽기)
- 부모 음성 샘플 업로드 및 ElevenLabs 연동
- PostgreSQL 기반 데이터 관리 및 오디오 캐시

## 디렉터리 구조

```text
EmoBook/
├─ backend/
│  ├─ api/                      # FastAPI 라우터 (Endpoints)
│  ├─ auth/                     # 인증 도메인 (JWT)
│  ├─ user/                     # 사용자 및 아이 프로필 도메인
│  ├─ story/                    # 동화 및 엔진 도메인 (Core, StoryAgent 등)
│  ├─ voice/                    # 음성 및 TTS 도메인 (ElevenLabs 연동)
│  ├─ storage/                  # 저장소 추상화 및 로컬 저장 구현
│  ├─ common/                   # 공통 설정 (DB, 의존성, Pydantic Base)
│  ├─ migrations/               # DB 마이그레이션 스크립트
│  ├─ local_storage/            # 개발용 업로드/생성 오디오 파일 저장소
│  ├─ tests/                    # Pytest 유닛 테스트 스위트
│  ├─ docker-compose.yml        # 로컬 PostgreSQL 실행 설정
│  ├─ requirements.txt          # Python 의존성
│  ├─ seed.py                   # 데모 사용자/동화/장면 시드 데이터
│  ├─ main.py                   # FastAPI 앱 진입점
│  └─ .env.example              # 환경변수 예시 파일
└─ README.md
```

## 백엔드 흐름

음성 샘플 업로드:

```text
api/voice_profiles_router.py
-> voice/voice_profile_service.py
-> storage/local_storage_service.py
-> voice/elevenlabs_client.py
-> voice/voice_profile_model.py
```

장면 TTS 생성:

```text
api/tts_router.py
-> voice/tts_service.py
-> story/story_model.py
-> voice/elevenlabs_client.py
-> storage/local_storage_service.py
-> voice/scene_audio_cache_model.py
```

동화 조회 및 세션 진행:

```text
api/stories_router.py, api/sessions_router.py
-> story/story_service.py, story/story_engine.py
-> story/story_model.py, story/story_scene_model.py
```

`backend/voice/`는 ElevenLabs 연동 경계입니다. 외부 provider 호출을 이 위치에 격리해두었기 때문에, 이후 Google TTS나 자체 TTS provider를 추가하더라도 핵심 동화 로직과 캐시 로직을 크게 바꾸지 않아도 됩니다.

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

PostgreSQL과 API 서버를 실행합니다.

```powershell
docker-compose up -d
python seed.py
uvicorn main:app --reload
```

### API 문서 확인 (서버 실행 후 접속)
* 👉 **Swagger UI (추천)**: [http://localhost:8000/docs](http://localhost:8000/docs)
  * 가장 일반적으로 쓰이는 인터랙티브 API 문서입니다. 화면에서 직접 `Try it out` 버튼을 눌러 API를 테스트해 볼 수 있습니다.
* 👉 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  * API 스펙을 한눈에 깔끔하게 읽기 좋은 형태의 문서입니다.
* 👉 **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
  * 프론트엔드 코드 제너레이터 등에 입력값으로 넣을 수 있는 순수 JSON 형태의 스펙 파일입니다.

## 주요 API 사용 흐름

1. 회원가입/로그인: `POST /api/v1/auth/signup` -> 토큰 획득
2. 아이 프로필 등록: `POST /api/v1/child-profiles`
3. 동화 시작: `POST /api/v1/stories/{story_id}/start`
4. 장면 진행: `POST /api/v1/sessions/{session_id}/next` 또는 `/choices`
5. 오디오 생성: `POST /api/v1/tts/generate`

## 환경변수

```env
EMOBOOK_DATABASE_URL=postgresql://emobook:emobook@localhost:5432/emobook
EMOBOOK_LOCAL_STORAGE_ROOT=backend/local_storage
EMOBOOK_PUBLIC_STORAGE_BASE_URL=/storage
EMOBOOK_ELEVENLABS_API_KEY=
EMOBOOK_ELEVENLABS_TTS_MODEL_ID=eleven_multilingual_v2
EMOBOOK_ELEVENLABS_OUTPUT_FORMAT=mp3_44100_128
```

## 참고 사항

현재 코드는 백엔드 MVP 단계입니다. 기획 문서에는 AI 장면 생성, Redis, Cloud Storage, Cloud Tasks가 포함되어 있습니다. 지금 구조는 도메인별로 격리되어 있어 이후 기능을 단계적으로 추가하기 쉽게 되어 있습니다.
