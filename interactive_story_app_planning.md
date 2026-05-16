# 인터랙티브 동화 앱 서비스 기획서
> **부모 목소리로 아이에게 동화를 읽어주는 앱** — MVP 기획서 v1.0

---

## 목차

1. [서비스 개요](#1-서비스-개요)
2. [문제 정의](#2-문제-정의)
3. [목표 사용자](#3-목표-사용자)
4. [핵심 가치](#4-핵심-가치)
5. [MVP 범위](#5-mvp-범위)
6. [제외 범위](#6-제외-범위)
7. [주요 기능](#7-주요-기능)
8. [사용자 플로우](#8-사용자-플로우)
9. [시스템 아키텍처](#9-시스템-아키텍처)
10. [기술 스택](#10-기술-스택)
11. [데이터베이스 설계](#11-데이터베이스-설계)
12. [API 명세 초안](#12-api-명세-초안)
13. [AI/TTS 처리 흐름](#13-aitts-처리-흐름)
14. [캐싱 전략](#14-캐싱-전략)
15. [비용 최적화 전략](#15-비용-최적화-전략)
16. [확장 전략](#16-확장-전략)
17. [개발 우선순위](#17-개발-우선순위)
18. [팀원 역할 분담 예시](#18-팀원-역할-분담-예시)
19. [리스크 및 대응 방안](#19-리스크-및-대응-방안)
20. [향후 고도화 방향](#20-향후-고도화-방향)

---

## 1. 서비스 개요

| 항목 | 내용 |
|------|------|
| 서비스명 | (가칭) StoryVoice |
| 한 줄 설명 | 부모의 목소리로 아이에게 인터랙티브 동화를 읽어주는 앱 |
| 플랫폼 | iOS / Android 모바일 앱 + 관리자 웹 |
| 인프라 | GCP (Google Cloud Platform) 기반 |
| 아키텍처 | 모듈형 모놀리스 (MVP) → 필요 시 MSA 전환 |
| AI 구조 | Story Engine Service 단일 조율자, Multi-Agent 미사용 |

부모가 자신의 목소리 샘플을 한 번 등록하면, 이후 아이가 동화를 선택할 때 부모의 목소리로 변환된 TTS 음성이 장면 단위로 재생됩니다. 아이는 선택지를 통해 동화의 흐름에 직접 참여합니다. 필요한 경우 LLM이 다음 장면을 동적으로 생성하며, 생성된 음성은 Cloud Storage에 캐싱되어 재사용됩니다.

---

## 2. 문제 정의

- 바쁜 부모는 아이에게 직접 동화를 읽어주지 못하는 상황이 많다.
- 기존 TTS 동화 앱은 기계적인 목소리로 아이의 정서적 유대감을 충족시키지 못한다.
- 단방향으로 듣기만 하는 동화는 아이의 참여도와 집중력을 낮춘다.
- 동화 선택의 폭이 좁고, 아이 연령·성향에 맞는 맞춤형 경험이 부족하다.

---

## 3. 목표 사용자

### Primary
- 3~8세 자녀를 둔 부모 (30~40대)
- 출장·야근 등으로 취침 전 동화를 직접 읽어주지 못하는 경우

### Secondary
- 아이 (3~8세): 선택지를 통해 능동적으로 동화에 참여하는 경험
- 조부모: 손자·손녀에게 자신의 목소리로 동화를 선물하고 싶은 경우

---

## 4. 핵심 가치

| 가치 | 설명 |
|------|------|
| 부모 목소리 | 아이에게 가장 친숙한 목소리로 동화를 들려줌 |
| 인터랙티브 참여 | 단순 청취가 아닌 선택지 기반 능동적 참여 |
| 감정적 유대 | 물리적 거리와 무관하게 부모-자녀 유대 경험 제공 |
| 맞춤형 경험 | 아이의 나이·성향에 맞는 언어·표현 사용 |
| 효율적 비용 | 음성 캐싱·pre-generation으로 불필요한 API 호출 최소화 |

---

## 5. MVP 범위

### 포함
- 회원가입 / 로그인 (이메일)
- 아이 프로필 등록 (이름, 나이, 선호 스타일)
- 부모 음성 샘플 업로드 및 voice_profile 생성
- DB에 저장된 동화 목록 조회 및 재생
- 장면 단위 텍스트 + 부모 목소리 TTS 오디오 재생
- 선택지 선택 → 다음 장면 이동
- 선택지에 해당하는 고정 장면이 없을 경우 LLM으로 동적 생성
- 생성된 오디오 Cloud Storage 캐싱 및 재사용
- 현재 장면 재생 중 다음 장면 오디오 pre-generation
- 관리자 웹: 동화/장면/선택지 등록 및 TTS 작업 상태 확인

### 핵심 설계 원칙 (MVP)
- LangGraph 미사용: 단순한 플로우이므로 Story Engine Service 코드로 직접 구현
- Multi-Agent 미사용: 하나의 Story Engine Service가 전체 흐름 조율
- 모듈형 모놀리스: MSA 전환을 고려한 내부 모듈 분리
- LLM 토큰 최적화: 현재 장면 + 최근 선택 기록 일부만 LLM에 전달 (3,000~7,000 tokens)

---

## 6. 제외 범위

| 항목 | 이유 |
|------|------|
| LangGraph / LangChain 워크플로우 | MVP 흐름이 단순, 오버엔지니어링 |
| Multi-Agent 구조 | Story Engine 단일 조율자로 충분 |
| RAG / Vector DB | 동화 데이터 규모가 작음, 추후 도입 |
| 실시간 스트리밍 TTS | MVP는 장면 단위 사전 생성으로 충분 |
| 소셜 로그인 (OAuth) | 1단계 제외, 2단계 이후 추가 |
| 추천 엔진 | 동화 수가 적은 초기에는 불필요 |
| 자체 TTS 모델 서버 | GPU 운영 비용, MVP는 외부 API 사용 |
| 결제 / 구독 | 0단계 제외, 서비스 안정화 후 추가 |

---

## 7. 주요 기능

### 7-1. 사용자 기능
- 회원가입 / 로그인
- 아이 프로필 등록 (다중 프로필 지원)
- 부모 음성 샘플 녹음 또는 파일 업로드
- 음성 프로필 생성 상태 확인
- 동화 목록 조회 (연령대 필터)
- 동화 시작 및 세션 생성
- 장면 텍스트 표시 + 부모 목소리 오디오 재생
- 선택지 선택 → 다음 장면 이동
- 동화 이어하기 (세션 복원)

### 7-2. 관리자 기능
- 동화 등록 / 수정 / 삭제
- 장면 등록 (텍스트, 감정 태그, 선택지)
- 선택지 등록 (다음 장면 연결 또는 LLM 생성 트리거)
- TTS 작업 상태 모니터링
- 사용자 / 음성 프로필 상태 확인

### 7-3. AI / LLM 기능
- 다음 장면 텍스트 동적 생성 (선택지에 고정 장면 없을 경우)
- 연령대에 맞는 어휘·표현 변환
- TTS 최적화 문장 정제
- 감정 태그: happy / calm / nervous / sad (문자열로 단순 처리)

### 7-4. Voice / TTS 기능
- 부모 음성 샘플을 외부 TTS/Voice Cloning API에 등록
- voice_profile_id 발급 및 저장
- 장면 텍스트 + voice_profile_id 기반 음성 생성
- 생성된 mp3/wav를 Cloud Storage에 저장
- audio_cache 테이블에 캐시 정보 저장
- 캐시 hit 시 TTS 호출 없이 audio_url 바로 반환

---

## 8. 사용자 플로우

### 8-1. 부모 음성 등록 플로우

```
1. 부모가 앱에서 [음성 등록] 선택
2. 음성 샘플 녹음 또는 파일 업로드 (10~30초 권장)
3. 백엔드가 원본 샘플을 Cloud Storage에 저장
4. Voice Profile Module이 외부 TTS/Voice API에 음성 프로필 생성 요청
5. provider_voice_id를 voice_profiles 테이블에 저장
6. status를 READY로 업데이트
7. 앱에 "음성 등록 완료" 알림
```

### 8-2. 동화 재생 플로우

```
1. 아이(또는 부모)가 동화 목록에서 동화 선택
2. POST /stories/{story_id}/start → user_story_sessions 생성
3. 첫 번째 scene 조회 (scene_key: 'start' 또는 order_index: 0)
4. Audio Cache Module: audio_cache 테이블에서 캐시 확인
   ├─ 캐시 hit → audio_url 바로 반환
   └─ 캐시 miss → TTS Job 생성 (비동기 큐 등록)
5. TTS Worker가 외부 TTS API 호출
6. 생성된 mp3를 Cloud Storage에 저장
7. audio_cache 테이블 업데이트
8. 앱이 audio_url로 오디오 재생
9. 재생 중 다음 장면 오디오 pre-generation 시작 (비동기)
```

### 8-3. 선택지 기반 진행 플로우

```
1. 아이가 선택지 선택
2. POST /sessions/{session_id}/choices → user_choice_logs에 저장
3. story_choices.next_scene_id 조회
   ├─ 고정 next_scene 있음 → 해당 scene 반환
   └─ 고정 next_scene 없음 → LLM 기반 동적 생성 플로우 진행
4. 다음 scene의 audio_cache 확인
   ├─ 캐시 hit → audio_url 반환
   └─ 캐시 miss → TTS Job 생성
5. 앱에서 다음 장면 텍스트 + 오디오 재생
```

### 8-4. LLM 기반 동적 생성 플로우

```
1. 선택지에 연결된 고정 next_scene_id가 없는 경우
2. Story Engine Service가 prompt 생성:
   - 현재 장면 텍스트 (scene.text)
   - 최근 선택 기록 3~5개 (user_choice_logs)
   - 아이 나이 (child_profiles.age)
   - 동화 스타일 (stories.description, child_profiles.preferred_style)
3. 외부 LLM API 호출 (예상 input: 3,000~7,000 tokens)
4. 생성된 장면 텍스트 + 선택지를 story_scenes / story_choices에 저장
5. TTS Job 생성 → 음성 생성 → Cloud Storage 저장
6. audio_url과 다음 scene 데이터를 앱에 반환
```

---

## 9. 시스템 아키텍처

### 9-1. 레이어 구조

```
┌──────────────────────────────────────────────┐
│                Client Layer                  │
│   Mobile App (React Native / Flutter)        │
│   Admin Web (React + Vite)                   │
└──────────────────┬───────────────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────────────┐
│              Edge / API Layer                │
│   Cloud Load Balancer                        │
│   Backend API / BFF (FastAPI or NestJS)      │
│   Auth Module (JWT)                          │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│           Core Backend Layer                 │
│   ┌────────────────────────────────────┐     │
│   │       Story Engine Service         │     │
│   │  - 현재 장면 조회                   │     │
│   │  - 사용자 선택 처리                 │     │
│   │  - 다음 장면 결정                   │     │
│   │  - 필요 시 LLM 호출                 │     │
│   │  - TTS 요청 관리                    │     │
│   │  - 오디오 캐시 확인                 │     │
│   └────────────────────────────────────┘     │
│   User/Profile Module                        │
│   Voice Profile Module                       │
│   Audio Cache Module                         │
│   Admin Module                               │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│              Async Layer                     │
│   Cloud Tasks / Pub/Sub                      │
│   TTS Worker                                 │
│   Pre-generation Worker                      │
└──────────────────┬───────────────────────────┘
                   │
┌─────────────┬────▼──────────┬────────────────┐
│  AI Provider│               │   Data Layer   │
│  ─────────  │               │  ───────────   │
│  LLM API   │               │  Cloud SQL     │
│  TTS/Voice │               │  Redis         │
│  Cloning   │               │  Cloud Storage │
│  API       │               │                │
└─────────────┴───────────────┴────────────────┘
```

### 9-2. 백엔드 디렉토리 구조

```
backend/
 ├─ api/              # FastAPI 라우터
 ├─ auth/             # JWT 인증
 ├─ user/             # 사용자/아이 프로필
 ├─ story/
 │   ├─ story_engine.py      # 핵심 조율자
 │   ├─ scene_service.py     # 장면 조회/저장
 │   ├─ choice_service.py    # 선택지 처리
 │   └─ prompt_builder.py    # LLM 프롬프트 생성
 ├─ voice/
 │   ├─ tts_service.py           # TTS API 연동
 │   ├─ voice_profile_service.py # 음성 프로필 관리
 │   └─ audio_cache_service.py   # 캐시 조회/저장
 ├─ storage/          # Cloud Storage 연동
 ├─ payment/          # (MVP 이후)
 └─ common/           # 공통 유틸리티
```

---

## 10. 기술 스택

| 영역 | MVP 선택 | 고도화 선택 |
|------|----------|-------------|
| Mobile | React Native 또는 Flutter | 동일 |
| Admin Web | React + Vite | 동일 |
| Backend | Python FastAPI 또는 Node.js NestJS | 동일 (모듈 분리) |
| LLM | Gemini API 또는 OpenAI API | 동일 또는 자체 파인튜닝 |
| TTS/Voice | ElevenLabs 또는 Google Cloud TTS | VoxCPM, OpenVoice, Qwen-TTS |
| DB | Cloud SQL (PostgreSQL) | 동일 + AlloyDB |
| Cache | Redis (Cloud Memorystore) | 동일 |
| Storage | Google Cloud Storage | 동일 |
| 비동기 큐 | Cloud Tasks 또는 Pub/Sub | 동일 |
| 배포 | Cloud Run | GKE + GPU Worker |
| CI/CD | GitHub Actions | 동일 |
| 모니터링 | Cloud Logging + Monitoring | 동일 + OpenTelemetry |
| Vector DB | 미사용 | Pinecone, pgvector, Weaviate |

---

## 11. 데이터베이스 설계

### users
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| email | VARCHAR UNIQUE | |
| password_hash | VARCHAR | |
| name | VARCHAR | |
| role | ENUM(user, admin) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### child_profiles
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| name | VARCHAR | |
| age | INT | |
| preferred_style | VARCHAR | 예: adventure, fairy_tale |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### stories
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| title | VARCHAR | |
| description | TEXT | |
| age_group | VARCHAR | 예: 3-5, 6-8 |
| cover_image_url | VARCHAR | |
| status | ENUM(draft, published) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### story_scenes
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| story_id | UUID FK → stories | |
| scene_key | VARCHAR | 예: start, chapter1_a |
| title | VARCHAR | |
| text | TEXT | 낭독 텍스트 |
| order_index | INT | |
| is_ending | BOOLEAN | |
| emotion_tag | VARCHAR | happy, calm, nervous, sad |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### story_choices
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| scene_id | UUID FK → story_scenes | |
| choice_text | VARCHAR | 선택지 표시 텍스트 |
| next_scene_id | UUID FK → story_scenes (nullable) | NULL이면 LLM 생성 |
| action_type | ENUM(fixed, llm_generate) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### user_story_sessions
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| child_profile_id | UUID FK → child_profiles | |
| story_id | UUID FK → stories | |
| current_scene_id | UUID FK → story_scenes | |
| status | ENUM(active, completed, abandoned) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### user_choice_logs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| session_id | UUID FK → user_story_sessions | |
| scene_id | UUID FK → story_scenes | |
| choice_id | UUID FK → story_choices | |
| selected_at | TIMESTAMP | |

### voice_profiles
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| profile_name | VARCHAR | |
| provider | VARCHAR | 예: elevenlabs, google_tts |
| provider_voice_id | VARCHAR | 외부 API 발급 ID |
| sample_audio_url | VARCHAR | Cloud Storage 원본 샘플 경로 |
| status | ENUM(processing, ready, failed) | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### audio_cache
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| voice_profile_id | UUID FK → voice_profiles | |
| story_id | UUID FK → stories | |
| scene_id | UUID FK → story_scenes | |
| text_hash | VARCHAR | SHA256(낭독 텍스트) |
| emotion_tag | VARCHAR | |
| audio_url | VARCHAR | Cloud Storage 경로 |
| provider | VARCHAR | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### tts_jobs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| voice_profile_id | UUID FK → voice_profiles | |
| scene_id | UUID FK → story_scenes | |
| text | TEXT | TTS 입력 텍스트 |
| status | ENUM(pending, processing, done, failed) | |
| audio_url | VARCHAR | 완료 시 저장 |
| error_message | TEXT | 실패 시 |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## 12. API 명세 초안

### 인증

#### `POST /auth/signup`
- **목적**: 신규 회원가입
- **Request**:
  ```json
  { "email": "user@example.com", "password": "secret123", "name": "홍길동" }
  ```
- **Response**:
  ```json
  { "user_id": "uuid", "email": "user@example.com", "token": "jwt_token" }
  ```
- **처리 흐름**: 이메일 중복 확인 → 비밀번호 해싱 → users 테이블 저장 → JWT 발급

#### `POST /auth/login`
- **목적**: 로그인 및 JWT 발급
- **Request**:
  ```json
  { "email": "user@example.com", "password": "secret123" }
  ```
- **Response**:
  ```json
  { "token": "jwt_token", "user_id": "uuid" }
  ```
- **처리 흐름**: 이메일 조회 → 비밀번호 검증 → JWT 발급

---

### 동화

#### `GET /stories`
- **목적**: 동화 목록 조회 (연령대 필터 지원)
- **Query Params**: `age_group=3-5`
- **Response**:
  ```json
  {
    "stories": [
      { "id": "uuid", "title": "토끼와 거북이", "age_group": "3-5", "cover_image_url": "https://..." }
    ]
  }
  ```
- **처리 흐름**: stories 테이블 조회 (status=published, age_group 필터)

#### `GET /stories/{story_id}`
- **목적**: 동화 상세 조회
- **Response**:
  ```json
  { "id": "uuid", "title": "...", "description": "...", "scene_count": 12 }
  ```

#### `POST /stories/{story_id}/start`
- **목적**: 동화 세션 시작
- **Request**:
  ```json
  { "child_profile_id": "uuid", "voice_profile_id": "uuid" }
  ```
- **Response**:
  ```json
  {
    "session_id": "uuid",
    "current_scene": {
      "id": "uuid", "text": "옛날 옛적에...", "emotion_tag": "calm",
      "audio_url": "https://storage.../scene1.mp3",
      "choices": [
        { "id": "uuid", "choice_text": "숲으로 간다" },
        { "id": "uuid", "choice_text": "마을로 간다" }
      ]
    }
  }
  ```
- **처리 흐름**: 세션 생성 → 첫 장면 조회 → audio_cache 확인 → 캐시 hit/miss 처리 → 응답

---

### 세션 / 선택지

#### `GET /sessions/{session_id}/current-scene`
- **목적**: 현재 장면 및 오디오 URL 조회
- **Response**: `POST /stories/{story_id}/start`의 current_scene과 동일 구조

#### `POST /sessions/{session_id}/choices`
- **목적**: 선택지 선택 및 다음 장면 반환
- **Request**:
  ```json
  { "choice_id": "uuid" }
  ```
- **Response**:
  ```json
  {
    "next_scene": {
      "id": "uuid", "text": "숲속에는...", "emotion_tag": "happy",
      "audio_url": "https://storage.../scene2.mp3",
      "choices": [...]
    }
  }
  ```
- **처리 흐름**:
  1. choice_id로 story_choices 조회
  2. user_choice_logs에 저장
  3. next_scene_id 존재 → 해당 scene 반환
  4. next_scene_id 없음 (action_type=llm_generate) → LLM 호출 → 장면 생성
  5. 다음 장면 audio_cache 확인 → miss면 TTS Job 생성
  6. 응답 반환

---

### 음성 프로필

#### `POST /voice-profiles`
- **목적**: 부모 음성 샘플 업로드 및 프로필 생성
- **Request**: multipart/form-data (audio_file + profile_name)
- **Response**:
  ```json
  { "voice_profile_id": "uuid", "status": "processing" }
  ```
- **처리 흐름**: 파일 Cloud Storage 업로드 → 외부 TTS API 프로필 생성 요청 → provider_voice_id 저장 → status=READY

#### `GET /voice-profiles`
- **목적**: 사용자의 음성 프로필 목록 조회
- **Response**:
  ```json
  { "profiles": [{ "id": "uuid", "profile_name": "아빠 목소리", "status": "ready" }] }
  ```

---

### TTS

#### `POST /tts/generate`
- **목적**: 특정 텍스트의 TTS 음성 수동 생성 (관리자 또는 pre-warm용)
- **Request**:
  ```json
  { "scene_id": "uuid", "voice_profile_id": "uuid", "text": "옛날 옛적에..." }
  ```
- **Response**:
  ```json
  { "tts_job_id": "uuid", "status": "pending" }
  ```
- **처리 흐름**: audio_cache 확인 → miss면 tts_jobs에 등록 → 비동기 큐 전달

#### `GET /audio-cache/{scene_id}`
- **목적**: 특정 장면의 캐시된 오디오 URL 조회
- **Query Params**: `voice_profile_id=uuid`
- **Response**:
  ```json
  { "audio_url": "https://storage.../scene1.mp3", "cache_hit": true }
  ```

---

### 관리자 API

#### `POST /admin/stories`
- **목적**: 동화 등록
- **Request**: `{ "title": "...", "description": "...", "age_group": "3-5" }`

#### `POST /admin/stories/{story_id}/scenes`
- **목적**: 장면 등록
- **Request**: `{ "scene_key": "chapter1_a", "text": "...", "emotion_tag": "happy", "order_index": 1 }`

#### `POST /admin/scenes/{scene_id}/choices`
- **목적**: 선택지 등록
- **Request**: `{ "choice_text": "숲으로 간다", "next_scene_id": "uuid", "action_type": "fixed" }`

#### `GET /admin/tts-jobs`
- **목적**: TTS 작업 목록 및 상태 확인
- **Response**: `{ "jobs": [{ "id": "uuid", "status": "done", "scene_id": "uuid" }] }`

---

## 13. AI/TTS 처리 흐름

### LLM 호출 구조

```
[Story Engine Service]
  ↓ prompt_builder.py
  {
    "system": "당신은 3~8세 아이를 위한 동화 작가입니다.",
    "context": {
      "current_scene_text": "숲 입구에 도착했습니다.",
      "recent_choices": ["숲으로 간다", "두려워하지 않는다"],
      "child_age": 5,
      "story_style": "adventure"
    },
    "instruction": "위 맥락에서 이어지는 다음 장면을 생성해주세요."
  }
  ↓
[외부 LLM API]  ← input: 약 3,000~7,000 tokens
  ↓
  {
    "scene_text": "숲 속에서 작은 동물 친구를 만났어요...",
    "choices": ["친구에게 인사한다", "조용히 지나친다"],
    "emotion_tag": "happy"
  }
```

**중요**: 전체 동화 데이터, 모든 장면, 모든 사용자 기록을 LLM에 넣지 않습니다. 현재 장면 텍스트 + 최근 선택 기록 일부 + 아이 나이/스타일만 전달합니다.

### TTS 처리 구조

```
[Audio Cache Module]
  ↓ text_hash + voice_profile_id로 audio_cache 조회
  ├─ 캐시 hit → audio_url 즉시 반환
  └─ 캐시 miss
       ↓
  [Cloud Tasks / Pub/Sub에 TTS Job 등록]
       ↓
  [TTS Worker]
       ↓ scene.text + voice_profile_id 전달 (약 100~800 tokens)
  [외부 TTS / Voice Cloning API]
       ↓
  mp3/wav 생성
       ↓
  [Cloud Storage에 저장]
       ↓
  [audio_cache 테이블 업데이트]
       ↓
  audio_url 반환
```

---

## 14. 캐싱 전략

| 캐시 대상 | 저장 위치 | 키 구조 | TTL |
|-----------|-----------|---------|-----|
| 오디오 파일 | Cloud Storage | `audio/{voice_profile_id}/{scene_id}/{text_hash}.mp3` | 영구 |
| 캐시 메타 정보 | audio_cache 테이블 | voice_profile_id + scene_id + text_hash | 영구 |
| 세션 상태 | Redis | `session:{session_id}` | 24h |
| TTS 작업 상태 | Redis | `tts_job:{job_id}` | 1h |
| audio_url 빠른 조회 | Redis | `audio_cache:{voice_profile_id}:{scene_id}` | 6h |

### 캐시 히트 판단 로직
1. `text_hash = SHA256(scene.text)`
2. `audio_cache` 테이블에서 `voice_profile_id + scene_id + text_hash` 조회
3. 존재하면 `audio_url` 즉시 반환 (TTS API 호출 없음)
4. 없으면 TTS Job 생성

### Pre-generation (다음 장면 음성 선제 생성)
- 현재 장면 오디오 재생 시작 시점에 비동기로 다음 가능한 장면들의 TTS Job 등록
- 선택지가 2개면 2개 모두 pre-generate 가능 (Cloud Tasks 활용)
- 아이가 선택지를 선택할 때 이미 오디오가 준비되어 있어 지연 시간 최소화

---

## 15. 비용 최적화 전략

| 전략 | 효과 |
|------|------|
| 장면 단위 텍스트만 LLM에 전달 | 매 요청 토큰 3,000~7,000으로 제한 (전체 동화 81,000 토큰 방지) |
| audio_cache 캐싱 | 동일 텍스트+음성프로필 조합 TTS 중복 호출 0 |
| pre-generation | 사용자 대기 시간 감소, 실시간 생성 부하 감소 |
| Cloud Storage 저장 | TTS API 재호출 없이 mp3 파일 재사용 |
| Redis 캐시 | DB 쿼리 감소, audio_url 빠른 반환 |
| voice_profile 최초 1회 생성 | 음성 등록 API 비용 최소화 |
| 고정 장면 DB 우선 사용 | LLM 호출은 동적 생성 필요 시에만 |

---

## 16. 확장 전략

### Phase 1 (MVP)
- Cloud Run 단일 서비스
- 외부 LLM API (Gemini/OpenAI)
- 외부 TTS API (ElevenLabs/Google TTS)
- Cloud SQL + Redis + Cloud Storage

### Phase 2 (성장기)
- 트래픽 증가 시 story, voice, auth 모듈을 독립 Cloud Run 서비스로 분리
- 소셜 로그인 추가 (OAuth)
- 결제/구독 모듈 추가
- 동화 추천 엔진 도입

### Phase 3 (고도화)
- GKE 전환 + GPU Worker 운영
- 자체 TTS/Voice Cloning 모델 서버 (VoxCPM, OpenVoice)
- Vector DB 도입 (RAG 기반 동화 생성)
- LangGraph 또는 워크플로우 엔진 도입 (복잡한 Multi-Agent 필요 시)
- 감정 분석 고도화 (단순 태그 → 모델 기반)
- 다국어 지원

---

## 17. 개발 우선순위

### 1단계: 기본 앱/백엔드 (2~3주)
- [ ] 회원가입 / 로그인 (JWT)
- [ ] 아이 프로필 등록
- [ ] 동화 목록 / 상세 조회
- [ ] 장면 조회
- [ ] 선택지 선택
- [ ] 세션 저장 및 복원

### 2단계: 동화 데이터 관리 (1~2주)
- [ ] 관리자 동화 등록
- [ ] 장면 등록 및 선택지 연결
- [ ] DB 기반 동화 재생 (고정 흐름)
- [ ] Admin Web 기본 UI

### 3단계: 음성/TTS (2~3주)
- [ ] 부모 음성 샘플 업로드
- [ ] voice_profile 생성 (외부 API 연동)
- [ ] TTS 생성 (장면 단위)
- [ ] Cloud Storage 저장
- [ ] audio_cache 테이블 적용
- [ ] 앱 오디오 플레이어 연동

### 4단계: LLM 연동 (2주)
- [ ] prompt_builder 구현
- [ ] 선택지 기반 다음 장면 동적 생성
- [ ] 생성된 장면 DB 저장
- [ ] 연령대 맞춤 문장 변환

### 5단계: 최적화 (1~2주)
- [ ] Redis 캐시 레이어
- [ ] TTS 비동기 큐 (Cloud Tasks)
- [ ] 다음 장면 pre-generation
- [ ] Cloud Logging / Monitoring 설정
- [ ] CI/CD (GitHub Actions + Cloud Run)

---

## 18. 팀원 역할 분담 예시

> 4명 기준

### Frontend / App 담당
- 모바일 앱 UI (React Native 또는 Flutter)
- 오디오 플레이어 컴포넌트
- 선택지 인터랙션 UI
- 로그인 / 아이 프로필 화면
- 음성 샘플 녹음 / 업로드 화면

### Backend / API 담당
- FastAPI 또는 NestJS 기반 API 구현
- JWT 인증 모듈
- Story Engine Service 구현 (scene_service, choice_service)
- DB 설계 및 마이그레이션 (Cloud SQL)
- 세션 관리

### AI / TTS 담당
- LLM 프롬프트 설계 (prompt_builder)
- 외부 LLM API 연동 (Gemini / OpenAI)
- 외부 TTS / Voice Cloning API 연동 (ElevenLabs 등)
- voice_profile 생성 흐름 구현
- audio_cache 처리 로직

### Infra / DevOps / Data 담당
- GCP 프로젝트 세팅 (Cloud Run, Cloud SQL, Cloud Storage, Redis)
- Cloud Tasks / Pub/Sub 설정
- GitHub Actions CI/CD 파이프라인
- Cloud Logging / Monitoring / Alerting
- Secret Manager 설정
- 데이터베이스 초기 데이터(동화 시드) 세팅

---

## 19. 리스크 및 대응 방안

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| 외부 TTS API 품질 미달 | 높음 | ElevenLabs, Google TTS 등 복수 Provider 평가 후 선택, 추후 자체 모델 전환 준비 |
| TTS 생성 지연 (3~10초) | 높음 | pre-generation + audio_cache로 대기 시간 최소화 |
| LLM 생성 장면 품질 이슈 | 중간 | prompt 세분화, 연령대별 프롬프트 템플릿, 사람이 검수한 시드 장면 충분히 확보 |
| 음성 프로필 생성 실패 | 중간 | 재시도 로직, 실패 시 사용자 안내, 기본 TTS 폴백 제공 |
| Cloud Storage 비용 증가 | 중간 | 오래된 캐시 정리 정책 (Cloud Storage Lifecycle), 인기 없는 오디오 만료 처리 |
| DB 쿼리 성능 저하 | 낮음 | Redis 캐시 적극 활용, 인덱스 최적화 |
| 개인정보 (음성 데이터) | 높음 | Cloud Storage 접근 제한, 데이터 암호화, 개인정보처리방침 수립 |

---

## 20. 향후 고도화 방향

- **자체 TTS 모델**: VoxCPM, OpenVoice, Qwen-TTS 등 GPU 서버에서 운영하여 비용 절감 및 품질 향상
- **감정 표현 고도화**: 단순 emotion_tag 문자열 → 모델 기반 감정 인식 및 음성 톤 조절
- **RAG 기반 동화 생성**: Vector DB 도입으로 기존 동화 스타일을 참조한 일관성 있는 장면 생성
- **Multi-Agent 구조**: Safety Agent(안전성 검수), Recommendation Agent(동화 추천), Voice Agent 분리
- **LangGraph 도입**: 장면 생성 → 안전성 검수 → 연령 검수 → 감정 태깅 등 복잡한 워크플로우 관리
- **추천 엔진**: 아이의 선택 패턴 분석을 통한 동화 추천
- **다국어 지원**: 영어, 중국어 등 다국어 TTS 및 동화 콘텐츠
- **구독 모델**: 무료 체험 + 유료 구독 (프리미엄 동화, 무제한 음성 생성)
- **소셜 기능**: 동화 완주 뱃지, 부모-자녀 공유 기능

---

*이 문서는 MVP 개발을 위한 기획서입니다. 버전: v1.0 | 작성일: 2025*
