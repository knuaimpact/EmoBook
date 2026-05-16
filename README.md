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
backend/
 ├─ api/                      # FastAPI 라우터 (Endpoints)
 │   ├─ auth_router.py        # 회원가입, 로그인 API
 │   ├─ child_profiles_router.py # 아이 프로필 관리 API
 │   ├─ sessions_router.py    # 동화 읽기 세션 진행 (Start, Next, Choices) API
 │   ├─ stories_router.py     # 동화 목록 및 상세 조회 API
 │   ├─ tts_router.py         # TTS 생성 및 작업 상태 조회 API
 │   └─ users_router.py       # 유저 관리 API
 ├─ auth/                     # 인증 도메인
 │   ├─ auth_service.py       # 패스워드 해싱 및 JWT 토큰 생성/검증 로직
 │   └─ auth_schema.py        # 로그인/회원가입 요청 및 응답 스키마
 ├─ user/                     # 사용자 및 아이 프로필 도메인
 │   ├─ user_model.py         # User DB 모델
 │   ├─ child_profile_model.py # ChildProfile DB 모델
 │   ├─ child_profile_service.py # 아이 프로필 관련 비즈니스 로직
 │   ├─ user_schema.py        # 사용자 데이터 스키마
 │   └─ child_profile_schema.py # 아이 프로필 데이터 스키마
 ├─ story/                    # 동화 및 엔진 도메인 (Core)
 │   ├─ story_model.py        # Story DB 모델
 │   ├─ story_scene_model.py  # StoryScene DB 모델
 │   ├─ story_choice_model.py # StoryChoice DB 모델
 │   ├─ story_generation_job_model.py # LLM 생성 작업 추적 모델
 │   ├─ user_story_session_model.py # 읽기 세션 상태 저장 모델
 │   ├─ user_choice_log_model.py # 아이의 선택 기록 로그 모델
 │   ├─ story_engine.py       # [중요] 전체 동화 진행 조율 및 세션 관리 로직
 │   ├─ story_service.py      # 동화 목록/상세 조회 서비스
 │   ├─ story_schema.py       # 동화 및 장면 데이터 스키마
 │   └─ session_schema.py     # 세션 진행 관련 요청/응답 스키마
 ├─ voice/                    # 음성 및 TTS 도메인
 │   ├─ voice_profile_model.py # 부모 음성 프로필 모델
 │   ├─ scene_audio_cache_model.py # 오디오 캐싱 데이터 모델
 │   ├─ tts_job_model.py       # TTS 작업 추적 모델
 │   ├─ elevenlabs_client.py   # ElevenLabs API 통신 클라이언트
 │   ├─ voice_profile_service.py # 음성 프로필 관리 서비스
 │   ├─ tts_service.py        # TTS 생성 및 파이프라인 관리 서비스
 │   ├─ voice_profile_schema.py # 음성 프로필 스키마
 │   └─ tts_schema.py         # TTS 요청/응답 스키마
 ├─ storage/                  # 파일 저장소 모듈
 │   ├─ storage_service.py    # 저장소 인터페이스 정의
 │   └─ local_storage_service.py # 로컬 파일 시스템 기반 저장소 구현
 ├─ common/                   # 공통 유틸리티 및 설정
 │   ├─ config.py             # 환경변수 및 앱 설정 (Pydantic Settings)
 │   ├─ database.py           # DB 연결 및 세션 설정 (SQLAlchemy)
 │   ├─ dependencies.py       # FastAPI 의존성 주입 (get_db, get_current_user 등)
 │   ├─ mixins.py             # DB 공통 필드 (CreatedAt, UpdatedAt)
 │   └─ common_schema.py      # 공통 Pydantic 베이스 클래스
 ├─ tests/                    # Pytest 유닛 테스트 스위트
 ├─ main.py                   # 애플리케이션 진입점 (FastAPI App 객체 생성)
 └─ seed.py                   # 초기 데이터 생성을 위한 시드 스크립트
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
