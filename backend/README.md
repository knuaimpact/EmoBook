# EmoBook Backend

부모의 목소리로 아이에게 인터랙티브 동화를 읽어주는 서비스, **EmoBook**의 백엔드 프로젝트이며,
도메인 중심의 모듈형 구조로 설계되었습니다.

## 🛠 기술 스택
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MySQL (SQLAlchemy 2.0 ORM)
- **Auth:** JWT (JSON Web Token)
- **AI/TTS:** ElevenLabs API, Gemini/OpenAI 
- **Validation:** Pydantic V2
- **Testing:** Pytest

## 📂 디렉토리 구조 및 파일 설명

```
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

## 🚀 시작하기

### 1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 필요한 설정값을 입력합니다 (기존 `.env.example` 참고).

### 3. 서버 실행
```bash
uvicorn main:app --reload
```

### 4. 테스트 실행
```bash
pytest tests/
```

### 5. API 문서 확인 (서버 실행 후 접속)
* 👉 **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
* 👉 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  * API 스펙을 한눈에 깔끔하게 읽기 좋은 형태의 문서
* 👉 **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
  * 프론트엔드 코드 제너레이터 등에 입력값으로 넣을 수 있는 순수 JSON 형태의 스펙 파일

