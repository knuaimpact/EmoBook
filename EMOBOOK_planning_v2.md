# 인터랙티브 동화 앱 서비스 기획서
> **부모 목소리로 아이에게 동화를 읽어주는 앱** — MVP 기획서 v1.1  
> 수정 반영: **단일 Story Agent + TTS Pipeline 구조**, **ElevenLabs API 고정**

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
13. [Story Agent / ElevenLabs TTS Pipeline 처리 흐름](#13-story-agent--elevenlabs-tts-pipeline-처리-흐름)
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
| 인프라 | GCP 기반 |
| 아키텍처 | 모듈형 모놀리스(MVP) → 필요 시 MSA 전환 |
| AI 구조 | **Story Engine 내부의 단일 Story Agent + ElevenLabs TTS Pipeline** |
| Voice/TTS Provider | **ElevenLabs API 고정** |

부모가 자신의 목소리 샘플을 한 번 등록하면, 이후 아이가 동화를 선택할 때 부모의 목소리로 변환된 TTS 음성이 장면 단위로 재생된다. 아이는 선택지를 통해 동화의 흐름에 직접 참여한다. 필요한 경우 **Story Agent**가 다음 장면, 선택지, 감정 태그를 동적으로 생성하며, 생성된 음성은 **ElevenLabs API**로 제작한 뒤 Cloud Storage에 저장하고 캐싱한다.

MVP에서는 Multi-Agent 구조를 사용하지 않는다. AI 생성은 Story Engine 내부의 **단일 Story Agent**가 담당하고, 음성 생성은 Agent가 아닌 **규칙 기반 TTS Pipeline**이 담당한다.

---

## 2. 문제 정의

- 바쁜 부모는 아이에게 직접 동화를 읽어주지 못하는 상황이 많다.
- 기존 TTS 동화 앱은 기계적인 목소리로 아이의 정서적 유대감을 충분히 충족시키지 못한다.
- 단방향으로 듣기만 하는 동화는 아이의 참여도와 집중력을 낮춘다.
- 동화 선택의 폭이 좁고, 아이 연령·성향에 맞는 맞춤형 경험이 부족하다.
- 부모 음성 데이터와 생성 오디오를 효율적으로 관리하지 않으면 비용과 개인정보 리스크가 커질 수 있다.

---

## 3. 목표 사용자

### Primary
- 3~8세 자녀를 둔 부모
- 출장·야근 등으로 취침 전 동화를 직접 읽어주지 못하는 보호자

### Secondary
- 아이: 선택지를 통해 능동적으로 동화에 참여하는 경험을 원하는 사용자
- 조부모: 손자·손녀에게 자신의 목소리로 동화를 선물하고 싶은 사용자

---

## 4. 핵심 가치

| 가치 | 설명 |
|------|------|
| 부모 목소리 | 아이에게 가장 친숙한 목소리로 동화를 들려줌 |
| 인터랙티브 참여 | 단순 청취가 아닌 선택지 기반 능동적 참여 |
| 감정적 유대 | 물리적 거리와 무관하게 부모-자녀 유대 경험 제공 |
| 맞춤형 경험 | 아이의 나이·성향에 맞는 언어·표현 사용 |
| 비용 효율 | 오디오 캐싱·pre-generation으로 불필요한 ElevenLabs 호출 최소화 |
| 구조 단순성 | 단일 Story Agent + TTS Pipeline으로 MVP 복잡도 감소 |

---

## 5. MVP 범위

### 포함
- 회원가입 / 로그인
- 아이 프로필 등록
- 부모 음성 샘플 업로드
- ElevenLabs 기반 voice profile 생성 및 `voice_id` 저장
- DB에 저장된 동화 목록 조회 및 재생
- 일반 동화(`linear`)와 인터랙티브 동화(`interactive`)를 같은 테이블 구조로 관리
- 장면 단위 텍스트 + 부모 목소리 TTS 오디오 재생
- 선택지 선택 → 다음 장면 이동
- 고정 다음 장면이 없을 경우 Story Agent로 다음 장면 동적 생성
- Story Agent가 장면 텍스트, 선택지, 감정 태그를 동시에 생성
- `emotion_tag`를 ElevenLabs `voice_settings`로 변환하는 TTS Pipeline
- 생성된 오디오 Cloud Storage 저장 및 audio_cache 재사용
- 현재 장면 재생 중 다음 장면 오디오 pre-generation
- 관리자 웹: 동화/장면/선택지 등록 및 TTS 작업 상태 확인

### 핵심 설계 원칙 (MVP)

- **LangGraph 미사용**: MVP 흐름은 단순하므로 Story Engine 코드로 직접 구현한다.
- **Multi-Agent 미사용**: Story Agent, Safety Agent, Voice Agent, RAG Agent 등으로 나누지 않는다.
- **단일 Story Agent 사용**: Story Agent는 장면 텍스트, 선택지, 감정 태그 생성을 담당한다.
- **TTS Pipeline은 Agent가 아님**: 감정 태그를 ElevenLabs `voice_settings`로 변환하고, 캐시 확인/작업 생성/저장을 수행하는 규칙 기반 파이프라인이다.
- **ElevenLabs API 고정**: MVP 음성 생성 Provider는 ElevenLabs로 통일한다.
- **Safety Agent 미사용**: 시스템 프롬프트와 출력 JSON Schema 검증으로 안전성을 제어한다.
- **모듈형 모놀리스**: 배포는 하나로 시작하되 내부 모듈은 `story`, `voice`, `storage`, `auth` 등으로 분리한다.
- **LLM 토큰 최적화**: 전체 동화가 아니라 현재 장면 + 최근 선택 기록 일부만 LLM에 전달한다.

---

## 6. 제외 범위

| 항목 | 이유 |
|------|------|
| LangGraph / LangChain 워크플로우 | MVP 흐름이 단순하여 오버엔지니어링 가능성 높음 |
| Multi-Agent 구조 | Story Agent 1개와 TTS Pipeline으로 충분함 |
| Safety Agent | 시스템 프롬프트 + JSON Schema 검증으로 1차 대응 |
| Voice Agent | ElevenLabs TTS Pipeline에서 규칙 기반으로 처리 가능 |
| RAG / Vector DB | 동화 데이터 규모가 작고, 초기에는 DB 기반 장면 관리로 충분 |
| 실시간 스트리밍 TTS | MVP는 장면 단위 사전 생성/캐싱 방식으로 충분 |
| 소셜 로그인 | 1단계 제외, 2단계 이후 추가 |
| 추천 엔진 | 동화 수가 적은 초기에는 불필요 |
| 자체 TTS 모델 서버 | GPU 운영 비용이 크므로 MVP에서는 ElevenLabs API 사용 |
| 결제 / 구독 | 서비스 안정화 후 추가 |

---

## 7. 주요 기능

### 7-1. 사용자 기능
- 회원가입 / 로그인
- 아이 프로필 등록
- 부모 음성 샘플 녹음 또는 파일 업로드
- ElevenLabs voice profile 생성 상태 확인
- 동화 목록 조회
- 동화 시작 및 세션 생성
- 장면 텍스트 표시 + 부모 목소리 오디오 재생
- 선택지 선택 → 다음 장면 이동
- 동화 이어하기

### 7-2. 관리자 기능
- 동화 등록 / 수정 / 삭제
- 장면 등록
- 선택지 등록
- 감정 태그 설정
- TTS 작업 상태 모니터링
- Story Agent 생성 결과 확인
- 사용자 / 음성 프로필 상태 확인

### 7-3. Story Agent 기능
- 아이 나이, 선호 스타일, 현재 장면, 최근 선택 기록 기반 다음 장면 생성
- 장면 단위 텍스트 생성
- 다음 선택지 2~3개 생성
- 장면별 감정 태그 생성
- TTS에 적합하도록 문장 길이와 표현 정제
- 안전한 콘텐츠 생성을 위한 시스템 프롬프트 적용
- 출력 JSON Schema 검증

Story Agent의 기본 출력 예시는 다음과 같다.

```json
{
  "scene_title": "별빛 숲 입구",
  "scene_text": "토끼는 조심스럽게 반짝이는 숲길을 걸었어요.",
  "emotion_tag": "calm",
  "choices": [
    { "choice_text": "반짝이는 길을 따라간다", "action_type": "go_to_scene" },
    { "choice_text": "풀숲의 소리를 확인한다", "action_type": "generate_scene" }
  ]
}
```

### 7-4. ElevenLabs TTS Pipeline 기능
- 부모 음성 샘플을 ElevenLabs에 등록하고 `voice_id`를 저장
- `scene_text`, `emotion_tag`, `voice_profile_id` 입력
- `emotion_tag`를 ElevenLabs `voice_settings`로 변환
- `audio_cache` 조회
- 캐시 hit 시 `audio_url` 즉시 반환
- 캐시 miss 시 `tts_jobs` 생성
- TTS Worker가 ElevenLabs Text to Speech API 호출
- 생성된 mp3/wav를 Cloud Storage에 저장
- `audio_cache` 테이블에 캐시 정보 저장

---

## 8. 사용자 플로우

### 8-1. 부모 음성 등록 플로우

```
1. 부모가 앱에서 [음성 등록] 선택
2. 음성 샘플 녹음 또는 파일 업로드
3. 백엔드가 원본 샘플을 Cloud Storage에 저장
4. Voice Profile Module이 ElevenLabs에 음성 프로필 생성 요청
5. ElevenLabs에서 발급된 voice_id를 voice_profiles.provider_voice_id에 저장
6. status를 ready로 업데이트
7. 앱에 "음성 등록 완료" 알림
```

### 8-2. 동화 재생 플로우

```
1. 아이 또는 부모가 동화 목록에서 동화 선택
2. POST /stories/{story_id}/start → user_story_sessions 생성
3. 첫 번째 scene 조회
4. TTS Pipeline이 audio_cache 확인
   ├─ 캐시 hit → audio_url 바로 반환
   └─ 캐시 miss → TTS Job 생성
5. TTS Worker가 ElevenLabs Text to Speech API 호출
6. 생성된 mp3를 Cloud Storage에 저장
7. audio_cache 테이블 업데이트
8. 앱이 audio_url로 오디오 재생
9. 재생 중 다음 가능한 장면 오디오 pre-generation 시작
```

### 8-3. 일반 동화 순차 진행 플로우

```
1. story_type=linear인 동화를 재생
2. 현재 장면 오디오 재생
3. 사용자가 [다음] 버튼 선택
4. POST /sessions/{session_id}/next 호출
5. Story Engine이 next_scene_id 또는 order_index 기준으로 다음 장면 조회
6. 다음 장면 audio_cache 확인
7. 앱에서 다음 장면 텍스트 + 오디오 재생
```

### 8-4. 선택지 기반 진행 플로우

```
1. 아이가 선택지 선택
2. POST /sessions/{session_id}/choices → user_choice_logs에 저장
3. story_choices.action_type 확인
   ├─ go_to_scene → next_scene_id 장면 반환
   ├─ generate_scene → Story Agent 호출
   └─ end_story → 세션 completed 처리
4. 다음 scene의 audio_cache 확인
   ├─ 캐시 hit → audio_url 반환
   └─ 캐시 miss → TTS Job 생성
5. 앱에서 다음 장면 텍스트 + 오디오 재생
```

### 8-5. Story Agent 기반 동적 생성 플로우

```
1. action_type=generate_scene인 선택지를 고른 경우
2. Story Engine이 story_generation_jobs 생성
3. Prompt Builder가 다음 정보를 기반으로 prompt 생성
   - 현재 장면 텍스트
   - 최근 선택 기록 3~5개
   - 아이 나이
   - 선호 스타일
   - 안전한 콘텐츠 생성을 위한 시스템 지시문
4. 외부 LLM API 호출
5. Story Agent 결과 JSON Schema 검증
6. 생성된 scene_text, choices, emotion_tag를 DB에 저장
7. TTS Pipeline이 ElevenLabs TTS Job 생성
8. audio_url과 다음 scene 데이터를 앱에 반환
```

---

## 9. 시스템 아키텍처

### 9-1. 레이어 구조

```
┌──────────────────────────────────────────────┐
│                Client Layer                  │
│   Mobile App                                 │
│   Admin Web                                  │
└──────────────────┬───────────────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────────────┐
│              Edge / API Layer                │
│   Cloud Load Balancer                        │
│   Backend API / BFF                          │
│   Auth Module                                │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│           Core Backend Layer                 │
│                                              │
│   Story Engine Service                       │
│   ├─ Session Manager                         │
│   ├─ Scene Resolver                          │
│   ├─ Choice Handler                          │
│   ├─ Story Agent                             │
│   │  ├─ 다음 장면 생성                       │
│   │  ├─ 선택지 생성                          │
│   │  ├─ 감정 태그 생성                       │
│   │  └─ 안전 프롬프트 적용                   │
│   └─ TTS Pipeline                            │
│      ├─ emotion_tag → voice_settings 변환    │
│      ├─ audio_cache 확인                     │
│      ├─ TTS Job 생성                         │
│      └─ audio_url 반환                       │
│                                              │
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
│  AI Provider│  Voice/TTS    │   Data Layer   │
│  ─────────  │  Provider     │  ───────────   │
│  LLM API    │  ElevenLabs   │  Cloud SQL     │
│             │  API          │  Redis         │
│             │               │  Cloud Storage │
└─────────────┴───────────────┴────────────────┘
```

> MVP에서는 LangGraph와 Multi-Agent 구조를 사용하지 않는다. Story Agent는 1개만 사용하며, TTS Pipeline은 Agent가 아니라 규칙 기반 처리 흐름이다.

### 9-2. 백엔드 디렉토리 구조

```
backend/
 ├─ api/                      # FastAPI/NestJS 라우터
 ├─ auth/                     # JWT 인증
 ├─ user/                     # 사용자/아이 프로필
 ├─ story/
 │   ├─ story_engine.py        # 전체 동화 진행 조율
 │   ├─ story_agent.py         # LLM 기반 장면/선택지/감정 태그 생성
 │   ├─ scene_service.py       # 장면 조회/저장
 │   ├─ choice_service.py      # 선택지 처리
 │   ├─ prompt_builder.py      # LLM 프롬프트 생성
 │   └─ story_output_schema.py # Story Agent 출력 검증
 ├─ voice/
 │   ├─ elevenlabs_client.py       # ElevenLabs API Client
 │   ├─ tts_pipeline.py            # TTS 처리 흐름
 │   ├─ emotion_mapper.py          # emotion_tag → voice_settings 변환
 │   ├─ tts_service.py             # TTS Job 처리
 │   ├─ voice_profile_service.py   # 음성 프로필 관리
 │   └─ audio_cache_service.py     # 캐시 조회/저장
 ├─ storage/
 │   └─ gcs_client.py          # Cloud Storage 연동
 ├─ payment/                  # MVP 이후
 └─ common/                   # 공통 유틸리티
```

---

## 10. 기술 스택

| 영역 | MVP 선택 | 고도화 선택 |
|------|----------|-------------|
| Mobile | React Native 또는 Flutter | 동일 |
| Admin Web | React + Vite | 동일 |
| Backend | Python FastAPI 또는 Node.js NestJS | 동일, 필요 시 서비스 분리 |
| LLM | Gemini API 또는 OpenAI API | 동일 또는 자체 파인튜닝 |
| TTS/Voice | **ElevenLabs API** | 자체 TTS 서버 또는 복수 Provider 확장 |
| DB | Cloud SQL(PostgreSQL) | AlloyDB 또는 Read Replica |
| Cache | Redis(Cloud Memorystore) | 동일 |
| Storage | Google Cloud Storage | 동일 |
| 비동기 큐 | Cloud Tasks 또는 Pub/Sub | 동일 |
| 배포 | Cloud Run | GKE + GPU Worker |
| CI/CD | GitHub Actions | 동일 |
| 모니터링 | Cloud Logging + Monitoring | OpenTelemetry 추가 |
| Vector DB | 미사용 | pgvector, Pinecone, Weaviate 등 |

### 환경변수 / Secret

```env
ELEVENLABS_API_KEY=...
ELEVENLABS_DEFAULT_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_DEFAULT_OUTPUT_FORMAT=mp3_44100_128
ELEVENLABS_TIMEOUT_SECONDS=60
```

- `ELEVENLABS_API_KEY`는 코드나 GitHub에 저장하지 않는다.
- GCP Secret Manager에 저장하고 Cloud Run 환경변수로 주입한다.

---

## 11. 데이터베이스 설계

### PK/FK 타입 기준

MVP 단계에서는 모든 내부 PK/FK를 `INTEGER` 기반 자동 증가 ID로 통일한다.

PostgreSQL 기준:

```sql
id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY
```

MySQL 기준:

```sql
id INT AUTO_INCREMENT PRIMARY KEY
```

초기 MVP에서는 `INTEGER`로 충분하며, 추후 로그성 테이블의 row 수가 크게 증가하면 `BIGINT` 전환 또는 파티셔닝을 검토한다.

### users
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 사용자 ID |
| email | VARCHAR UNIQUE | 로그인 이메일 |
| password_hash | VARCHAR | 비밀번호 해시 |
| name | VARCHAR | 표시 이름 |
| role | ENUM(user, admin) | 사용자 권한 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### child_profiles
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 아이 프로필 ID |
| user_id | INTEGER FK → users | 보호자 계정 |
| name | VARCHAR | 아이 이름 |
| age | INT | 아이 나이 |
| preferred_style | VARCHAR | adventure, fairy_tale 등 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### stories
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 동화 ID |
| title | VARCHAR | 제목 |
| description | TEXT | 설명 |
| age_group | VARCHAR | 예: 3-5, 6-8 |
| cover_image_url | VARCHAR | 표지 이미지 URL |
| story_type | ENUM(linear, interactive) | 일반 동화 / 인터랙티브 동화 구분 |
| status | ENUM(draft, published) | 공개 상태 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### story_scenes
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 장면 ID |
| story_id | INTEGER FK → stories | 소속 동화 |
| parent_scene_id | INTEGER FK → story_scenes nullable | 동적 생성 장면의 부모 장면 |
| scene_key | VARCHAR | 예: start, chapter1_a |
| title | VARCHAR | 장면 제목 |
| text | TEXT | 낭독 텍스트 |
| order_index | INT | 기본 정렬 순서 |
| next_scene_id | INTEGER FK → story_scenes nullable | 일반 동화의 다음 장면. 없으면 order_index 기반 조회 |
| is_ending | BOOLEAN | 엔딩 여부 |
| emotion_tag | VARCHAR | calm, happy, nervous, sad, excited 등 |
| generation_type | ENUM(static, llm_generated) | 고정 장면 / Story Agent 생성 장면 구분 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### story_choices
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 선택지 ID |
| scene_id | INTEGER FK → story_scenes | 소속 장면 |
| choice_text | VARCHAR | 선택지 표시 텍스트 |
| next_scene_id | INTEGER FK → story_scenes nullable | 다음 장면. 없으면 생성 가능 |
| action_type | ENUM(go_to_scene, generate_scene, end_story) | 선택지 동작 방식 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### user_story_sessions
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 세션 ID |
| user_id | INTEGER FK → users | 사용자 ID |
| child_profile_id | INTEGER FK → child_profiles | 아이 프로필 ID |
| story_id | INTEGER FK → stories | 동화 ID |
| current_scene_id | INTEGER FK → story_scenes | 현재 장면 |
| status | ENUM(active, completed, abandoned) | 세션 상태 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### user_choice_logs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 선택 로그 ID |
| session_id | INTEGER FK → user_story_sessions | 세션 ID |
| scene_id | INTEGER FK → story_scenes | 선택 당시 장면 |
| choice_id | INTEGER FK → story_choices | 선택한 선택지 |
| selected_at | TIMESTAMP | 선택 시각 |

### voice_profiles
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 음성 프로필 ID |
| user_id | INTEGER FK → users | 사용자 ID |
| profile_name | VARCHAR | 예: 아빠 목소리 |
| provider | VARCHAR | elevenlabs 고정 |
| provider_voice_id | VARCHAR | ElevenLabs `voice_id` |
| sample_audio_url | VARCHAR | Cloud Storage 원본 샘플 경로 |
| provider_metadata | JSON | ElevenLabs voice metadata, clone 설정 등 |
| status | ENUM(processing, ready, failed) | 음성 프로필 상태 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### audio_cache
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 오디오 캐시 ID |
| voice_profile_id | INTEGER FK → voice_profiles | 사용할 음성 프로필 |
| story_id | INTEGER FK → stories | 동화 ID |
| scene_id | INTEGER FK → story_scenes | 장면 ID |
| text_hash | VARCHAR | SHA256(낭독 텍스트) |
| emotion_tag | VARCHAR | 장면 감정 태그 |
| voice_settings_hash | VARCHAR | ElevenLabs voice_settings 해시 |
| model_id | VARCHAR | ElevenLabs 모델 ID |
| output_format | VARCHAR | 예: mp3_44100_128 |
| audio_url | VARCHAR | Cloud Storage 경로 |
| duration_ms | INT | 오디오 길이 |
| provider | VARCHAR | elevenlabs |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

추천 UNIQUE KEY:

```sql
UNIQUE (
  voice_profile_id,
  scene_id,
  text_hash,
  emotion_tag,
  voice_settings_hash,
  model_id,
  output_format
)
```

### tts_jobs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | TTS 작업 ID |
| voice_profile_id | INTEGER FK → voice_profiles | 사용할 음성 프로필 |
| scene_id | INTEGER FK → story_scenes | 장면 ID |
| text | TEXT | TTS 입력 텍스트 |
| emotion_tag | VARCHAR | 감정 태그 |
| model_id | VARCHAR | ElevenLabs 모델 ID |
| voice_settings | JSON | ElevenLabs voice settings |
| output_format | VARCHAR | 출력 포맷 |
| status | ENUM(pending, processing, done, failed) | 작업 상태 |
| provider_job_id | VARCHAR | 외부 Provider 작업 ID 또는 추적 ID |
| audio_url | VARCHAR | 완료 시 저장 경로 |
| error_message | TEXT | 실패 메시지 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

### story_generation_jobs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | Story Agent 생성 작업 ID |
| session_id | INTEGER FK → user_story_sessions | 세션 ID |
| story_id | INTEGER FK → stories | 동화 ID |
| source_scene_id | INTEGER FK → story_scenes | 생성이 시작된 원본 장면 |
| choice_id | INTEGER FK → story_choices | 사용자가 선택한 선택지 |
| generated_scene_id | INTEGER FK → story_scenes nullable | 생성 완료된 장면 |
| status | ENUM(pending, processing, done, failed) | 작업 상태 |
| provider | VARCHAR | LLM Provider |
| model | VARCHAR | LLM 모델명 |
| input_tokens | INT | 입력 토큰 수 |
| output_tokens | INT | 출력 토큰 수 |
| prompt_summary | TEXT | 프롬프트 요약 또는 마스킹된 내용 |
| error_message | TEXT | 실패 메시지 |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |

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
  { "user_id": 1, "email": "user@example.com", "token": "jwt_token" }
  ```
- **처리 흐름**: 이메일 중복 확인 → 비밀번호 해싱 → users 저장 → JWT 발급

#### `POST /auth/login`
- **목적**: 로그인 및 JWT 발급
- **Request**:
  ```json
  { "email": "user@example.com", "password": "secret123" }
  ```
- **Response**:
  ```json
  { "token": "jwt_token", "user_id": 1 }
  ```

---

### 동화

#### `GET /stories`
- **목적**: 동화 목록 조회
- **Query Params**: `age_group=3-5`
- **Response**:
  ```json
  {
    "stories": [
      { "id": 1, "title": "토끼와 거북이", "age_group": "3-5", "cover_image_url": "https://..." }
    ]
  }
  ```

#### `GET /stories/{story_id}`
- **목적**: 동화 상세 조회
- **Response**:
  ```json
  { "id": 1, "title": "...", "description": "...", "scene_count": 12 }
  ```

#### `POST /stories/{story_id}/start`
- **목적**: 동화 세션 시작
- **Request**:
  ```json
  { "child_profile_id": 1, "voice_profile_id": 1 }
  ```
- **Response**:
  ```json
  {
    "session_id": 1,
    "current_scene": {
      "id": 1,
      "text": "옛날 옛적에...",
      "emotion_tag": "calm",
      "audio_url": "https://storage.../scene1.mp3",
      "choices": [
        { "id": 1, "choice_text": "숲으로 간다" },
        { "id": 1, "choice_text": "마을로 간다" }
      ]
    }
  }
  ```
- **처리 흐름**: 세션 생성 → 첫 장면 조회 → TTS Pipeline 캐시 확인 → 캐시 hit/miss 처리 → 응답

---

### 세션 / 선택지

#### `GET /sessions/{session_id}/current-scene`
- **목적**: 현재 장면 및 오디오 URL 조회
- **Response**: `POST /stories/{story_id}/start`의 `current_scene`과 동일 구조

#### `POST /sessions/{session_id}/next`
- **목적**: 일반 동화(`story_type=linear`)에서 다음 장면으로 이동
- **Request**:
  ```json
  { "current_scene_id": 1 }
  ```
- **Response**:
  ```json
  {
    "next_scene": {
      "id": 2,
      "text": "토끼는 다음 숲길로 걸어갔어요.",
      "emotion_tag": "calm",
      "audio_url": "https://storage.../scene2.mp3",
      "is_ending": false
    }
  }
  ```
- **처리 흐름**:
  1. session_id로 현재 세션과 story_type 확인
  2. `story_type=linear`이면 current_scene의 next_scene_id 또는 order_index + 1 장면 조회
  3. 다음 장면 audio_cache 확인
  4. 캐시 miss면 ElevenLabs TTS Job 생성
  5. current_scene_id 업데이트 후 응답 반환

#### `POST /sessions/{session_id}/choices`
- **목적**: 선택지 선택 및 다음 장면 반환
- **Request**:
  ```json
  { "choice_id": 1 }
  ```
- **Response**:
  ```json
  {
    "next_scene": {
      "id": 1,
      "text": "숲속에는...",
      "emotion_tag": "happy",
      "audio_url": "https://storage.../scene2.mp3",
      "choices": []
    }
  }
  ```
- **처리 흐름**:
  1. choice_id로 story_choices 조회
  2. user_choice_logs에 저장
  3. `action_type=go_to_scene` → next_scene_id 장면 반환
  4. `action_type=generate_scene` → Story Agent 호출 → 장면/선택지/emotion_tag 생성 → story_generation_jobs 기록
  5. `action_type=end_story` → 세션 완료 처리
  6. 다음 장면 audio_cache 확인 → miss면 ElevenLabs TTS Job 생성
  7. 응답 반환

---

### 음성 프로필

#### `POST /voice-profiles`
- **목적**: 부모 음성 샘플 업로드 및 ElevenLabs voice profile 생성
- **Request**: multipart/form-data
  - `audio_file`
  - `profile_name`
- **Response**:
  ```json
  {
    "voice_profile_id": 1,
    "provider": "elevenlabs",
    "provider_voice_id": "elevenlabs_voice_id",
    "status": "processing"
  }
  ```
- **처리 흐름**: 파일 Cloud Storage 업로드 → ElevenLabs 음성 등록 요청 → `provider_voice_id` 저장 → 상태 업데이트

#### `GET /voice-profiles`
- **목적**: 사용자의 음성 프로필 목록 조회
- **Response**:
  ```json
  { "profiles": [{ "id": 1, "profile_name": "아빠 목소리", "provider": "elevenlabs", "status": "ready" }] }
  ```

---

### TTS

#### `POST /tts/generate`
- **목적**: 특정 텍스트의 ElevenLabs TTS 음성 생성
- **Request**:
  ```json
  {
    "scene_id": 1,
    "voice_profile_id": 1,
    "text": "토끼는 조심스럽게 숲속으로 걸어갔어요.",
    "emotion_tag": "calm",
    "model_id": "eleven_multilingual_v2",
    "output_format": "mp3_44100_128"
  }
  ```
- **Response**:
  ```json
  { "tts_job_id": 1, "status": "pending", "provider": "elevenlabs" }
  ```
- **처리 흐름**:
  1. voice_profile_id로 ElevenLabs voice_id 조회
  2. emotion_tag를 voice_settings로 변환
  3. text_hash + voice_settings_hash 생성
  4. audio_cache 조회
  5. 캐시 miss면 tts_jobs 생성
  6. Cloud Tasks/PubSub에 TTS 작업 등록
  7. Worker가 ElevenLabs Text to Speech API 호출
  8. 생성된 mp3를 Cloud Storage에 저장
  9. audio_cache 저장

#### `GET /tts-jobs/{tts_job_id}`
- **목적**: TTS 생성 상태 조회
- **Response**:
  ```json
  { "tts_job_id": 1, "status": "done", "audio_url": "https://storage.../scene.mp3" }
  ```

#### `GET /audio-cache/{scene_id}`
- **목적**: 특정 장면의 캐시된 오디오 URL 조회
- **Query Params**: `voice_profile_id=1&emotion_tag=calm`
- **Response**:
  ```json
  { "audio_url": "https://storage.../scene1.mp3", "cache_hit": true }
  ```

---

### Story Agent 작업

#### `GET /story-generation-jobs/{job_id}`
- **목적**: Story Agent 생성 작업 상태 조회
- **Response**:
  ```json
  {
    "job_id": 1,
    "status": "done",
    "generated_scene_id": 101,
    "input_tokens": 4200,
    "output_tokens": 900
  }
  ```

---

### 관리자 API

#### `POST /admin/stories`
- **목적**: 동화 등록
- **Request**: `{ "title": "...", "description": "...", "age_group": "3-5", "story_type": "linear" }`

#### `POST /admin/stories/{story_id}/scenes`
- **목적**: 장면 등록
- **Request**:
  ```json
  {
    "scene_key": "chapter1_a",
    "text": "...",
    "emotion_tag": "happy",
    "order_index": 1,
    "generation_type": "static"
  }
  ```

#### `POST /admin/scenes/{scene_id}/choices`
- **목적**: 선택지 등록
- **Request**:
  ```json
  {
    "choice_text": "숲으로 간다",
    "next_scene_id": 2,
    "action_type": "go_to_scene"
  }
  ```

#### `GET /admin/tts-jobs`
- **목적**: TTS 작업 목록 및 상태 확인
- **Response**: `{ "jobs": [{ "id": 1, "status": "done", "scene_id": 1 }] }`

#### `GET /admin/story-generation-jobs`
- **목적**: Story Agent 생성 작업 목록 및 상태 확인
- **Response**: `{ "jobs": [{ "id": 1, "status": "done", "generated_scene_id": 101 }] }`

---

## 13. Story Agent / ElevenLabs TTS Pipeline 처리 흐름

### 13-1. Story Agent 호출 구조

```
[Story Engine Service]
  ↓
[Prompt Builder]
  - 아이 나이
  - 선호 스타일
  - 현재 장면 텍스트
  - 최근 선택 기록 3~5개
  - 안전한 콘텐츠 생성을 위한 시스템 지시문
  ↓
[Story Agent / LLM API]
  ↓
{
  "scene_text": "숲 속에서 작은 동물 친구를 만났어요...",
  "choices": ["친구에게 인사한다", "조용히 지나친다"],
  "emotion_tag": "happy"
}
  ↓
[JSON Schema Validation]
  ↓
[story_scenes / story_choices 저장]
  ↓
[story_generation_jobs 완료 처리]
```

**중요**: 전체 동화 데이터, 모든 장면, 모든 사용자 기록을 LLM에 넣지 않는다. 현재 장면 텍스트 + 최근 선택 기록 일부 + 아이 나이/스타일만 전달한다.

### 13-2. ElevenLabs TTS Pipeline 구조

```
[Audio Cache Module]
  ↓ voice_profile_id + scene_id + text_hash + emotion_tag + voice_settings_hash 조회
  ├─ 캐시 hit → audio_url 즉시 반환
  └─ 캐시 miss
       ↓
  [Emotion Mapper]
       ↓ emotion_tag → ElevenLabs voice_settings 변환
  [Cloud Tasks / Pub/Sub에 TTS Job 등록]
       ↓
  [TTS Worker]
       ↓ voice_id + scene.text + model_id + voice_settings 전달
  [ElevenLabs Text to Speech API]
       ↓
  mp3/wav 생성
       ↓
  [Cloud Storage에 저장]
       ↓
  [audio_cache 테이블 업데이트]
       ↓
  audio_url 반환
```

### 13-3. Emotion Mapper

`emotion_tag`는 ElevenLabs의 직접 emotion 파라미터가 아니라, 서비스 내부 제어값이다. TTS Pipeline은 이를 `voice_settings`와 문장 표현 조정에 활용한다.

| emotion_tag | voice_settings 방향 | 문장/낭독 방향 |
|------------|--------------------|----------------|
| calm | stability 높음, style 낮음 | 차분하고 안정적인 낭독 |
| happy | stability 중간, style 중간 | 밝고 부드러운 표현 |
| nervous | stability 중간 이하, style 중간 | 조심스럽고 긴장감 있는 표현 |
| sad | stability 높음, style 낮음 | 느리고 차분한 표현 |
| excited | stability 낮음, style 높음 | 활기차고 빠른 리듬 |

예시:

```json
{
  "emotion_tag": "happy",
  "voice_settings": {
    "stability": 0.55,
    "similarity_boost": 0.8,
    "style": 0.45,
    "use_speaker_boost": true
  }
}
```

---

## 14. 캐싱 전략

| 캐시 대상 | 저장 위치 | 키 구조 | TTL |
|-----------|-----------|---------|-----|
| 오디오 파일 | Cloud Storage | `audio/{voice_profile_id}/{scene_id}/{emotion_tag}/{text_hash}_{voice_settings_hash}.mp3` | 영구 또는 정책 기반 |
| 캐시 메타 정보 | audio_cache 테이블 | voice_profile_id + scene_id + text_hash + emotion_tag + voice_settings_hash + model_id + output_format | 영구 |
| 세션 상태 | Redis | `session:{session_id}` | 24h |
| TTS 작업 상태 | Redis | `tts_job:{job_id}` | 1h |
| audio_url 빠른 조회 | Redis | `audio_cache:{voice_profile_id}:{scene_id}:{emotion_tag}` | 6h |
| Story Agent 작업 상태 | Redis | `story_generation_job:{job_id}` | 1h |

### 캐시 히트 판단 로직
1. `text_hash = SHA256(scene.text)`
2. `emotion_tag`를 ElevenLabs `voice_settings`로 변환
3. `voice_settings_hash = SHA256(JSON.stringify(voice_settings))`
4. `audio_cache`에서 `voice_profile_id + scene_id + text_hash + emotion_tag + voice_settings_hash + model_id + output_format` 조회
5. 존재하면 `audio_url` 즉시 반환
6. 없으면 TTS Job 생성

### Pre-generation
- 현재 장면 오디오 재생 시작 시점에 다음 가능한 장면들의 TTS Job을 비동기로 등록한다.
- 선택지가 2개면 2개 모두 pre-generate 가능하다.
- 단, ElevenLabs 비용 증가를 막기 위해 pre-generation은 다음 1-depth까지만 기본 적용한다.
- 사용자가 자주 선택하지 않는 분기까지 과도하게 생성하지 않는다.

---

## 15. 비용 최적화 전략

| 전략 | 효과 |
|------|------|
| 장면 단위 텍스트만 LLM에 전달 | 전체 동화 81,000 토큰 입력 방지 |
| Story Agent 호출 로그 저장 | input/output token 기록으로 LLM 비용 추적 |
| ElevenLabs audio_cache 적용 | 동일 텍스트+음성+감정 설정 조합의 TTS 중복 호출 방지 |
| emotion_tag 기반 캐시 키 | 같은 문장이라도 감정/톤이 다르면 다른 오디오로 관리 |
| TTS Pipeline 분리 | 음성 생성 과정에서 불필요한 LLM 호출 방지 |
| pre-generation 제한 | 대기 시간은 줄이되 ElevenLabs 호출 폭증 방지 |
| Cloud Storage 저장 | ElevenLabs 재호출 없이 mp3 파일 재사용 |
| Redis 캐시 | DB 쿼리 감소, audio_url 빠른 반환 |
| voice_profile 최초 1회 생성 | 음성 등록 API 비용 최소화 |
| 고정 장면 DB 우선 사용 | LLM 호출은 동적 생성 필요 시에만 수행 |

---

## 16. 확장 전략

### Phase 1 (MVP)
- Cloud Run 단일 서비스
- 외부 LLM API
- ElevenLabs API
- Cloud SQL + Redis + Cloud Storage
- Cloud Tasks / Pub/Sub 기반 TTS 비동기 처리

### Phase 2 (성장기)
- 트래픽 증가 시 story, voice, auth 모듈을 독립 Cloud Run 서비스로 분리
- 소셜 로그인 추가
- 결제/구독 모듈 추가
- 동화 추천 엔진 도입
- ElevenLabs 사용량 모니터링 및 비용 정책 강화

### Phase 3 (고도화)
- GKE 전환 + GPU Worker 운영
- 자체 TTS/Voice Cloning 모델 서버 실험
- 복수 TTS Provider 추상화
- Vector DB 도입
- LangGraph 또는 워크플로우 엔진 도입
- 필요 시 Safety Agent, Recommendation Agent 등 Multi-Agent 구조 확장
- 감정 표현 고도화
- 다국어 지원

---

## 17. 개발 우선순위

### 1단계: 기본 앱/백엔드 (2~3주)
- [ ] 회원가입 / 로그인
- [ ] 아이 프로필 등록
- [ ] 동화 목록 / 상세 조회
- [ ] 장면 조회
- [ ] 선택지 선택
- [ ] 세션 저장 및 복원

### 2단계: 동화 데이터 관리 (1~2주)
- [ ] 관리자 동화 등록
- [ ] 장면 등록 및 선택지 연결
- [ ] 감정 태그 입력
- [ ] DB 기반 동화 재생
- [ ] Admin Web 기본 UI

### 3단계: ElevenLabs 음성/TTS (2~3주)
- [ ] 부모 음성 샘플 업로드
- [ ] ElevenLabs voice profile 생성
- [ ] `provider_voice_id` 저장
- [ ] `elevenlabs_client.py` 구현
- [ ] `emotion_mapper.py` 구현
- [ ] `tts_pipeline.py` 구현
- [ ] ElevenLabs TTS 생성
- [ ] Cloud Storage 저장
- [ ] `voice_settings_hash` 기반 audio_cache 적용
- [ ] 앱 오디오 플레이어 연동

### 4단계: Story Agent / LLM 연동 (2주)
- [ ] `story_agent.py` 구현
- [ ] `prompt_builder.py` 구현
- [ ] Story Agent 출력 JSON Schema 정의
- [ ] scene_text, choices, emotion_tag 동시 생성
- [ ] story_generation_jobs 기록
- [ ] 생성된 장면/선택지 DB 저장
- [ ] 시스템 프롬프트 기반 안전성 제어
- [ ] 실패 시 fallback 처리

### 5단계: 최적화 (1~2주)
- [ ] Redis 캐시 레이어
- [ ] TTS 비동기 큐
- [ ] 다음 장면 pre-generation
- [ ] ElevenLabs 사용량 로그
- [ ] Cloud Logging / Monitoring 설정
- [ ] CI/CD

---

## 18. 팀원 역할 분담 예시

> 4명 기준

### Frontend / App 담당
- 모바일 앱 UI
- 오디오 플레이어 컴포넌트
- 선택지 인터랙션 UI
- 로그인 / 아이 프로필 화면
- 음성 샘플 녹음 / 업로드 화면

### Backend / API 담당
- API 구현
- JWT 인증 모듈
- Story Engine Service 구현
- DB 설계 및 마이그레이션
- 세션 관리

### AI / Story Agent / TTS 담당
- Story Agent 프롬프트 설계
- Story Agent 출력 JSON Schema 설계
- 외부 LLM API 연동
- ElevenLabs API 연동
- Emotion Mapper 설계
- TTS Pipeline 구현
- audio_cache 처리 로직

### Infra / DevOps / Data 담당
- GCP 프로젝트 세팅
- Cloud Run 배포
- Cloud SQL
- Cloud Storage
- Redis
- Cloud Tasks / Pub/Sub
- Secret Manager
- GitHub Actions CI/CD
- Cloud Logging / Monitoring
- 데이터베이스 초기 데이터 세팅

---

## 19. 리스크 및 대응 방안

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|-----------|
| ElevenLabs API 비용 증가 | 높음 | audio_cache, pre-generation 제한, 월별 사용량 모니터링 |
| ElevenLabs API 장애/지연 | 중간 | 재시도 로직, 기본 음성 fallback, 실패 시 텍스트 먼저 제공 |
| 부모 음성 클론 품질 편차 | 높음 | 업로드 가이드 제공, 샘플 길이/잡음 검증, 재등록 기능 |
| 감정 태그 반영 한계 | 중간 | emotion_tag는 내부 제어값으로 사용하고 텍스트 표현 + voice_settings 함께 튜닝 |
| Story Agent 출력 형식 불안정 | 중간 | JSON Schema 강제, 재시도 로직, 실패 시 고정 장면 fallback |
| LLM 생성 장면 품질 이슈 | 중간 | prompt 세분화, 연령대별 템플릿, 사람이 검수한 시드 장면 확보 |
| TTS 생성 지연 | 높음 | pre-generation + audio_cache로 대기 시간 최소화 |
| 음성 프로필 생성 실패 | 중간 | 재시도 로직, 실패 시 안내, 기본 TTS fallback 제공 |
| Cloud Storage 비용 증가 | 중간 | 오래된 캐시 정리 정책, Lifecycle Rule 적용 |
| 개인정보/음성 데이터 | 높음 | Cloud Storage 접근 제한, 암호화, 동의 절차, 삭제 요청 기능 |
| API Key 노출 | 높음 | Secret Manager 사용, GitHub 커밋 금지, 권한 최소화 |

---

## 20. 향후 고도화 방향

- **자체 TTS 모델**: VoxCPM, OpenVoice, Qwen-TTS 등 GPU 서버에서 실험
- **복수 Provider 추상화**: ElevenLabs 외 Provider를 교체 가능하게 adapter 구조 확장
- **감정 표현 고도화**: 단순 emotion_tag → 문장/음성 톤 자동 튜닝
- **RAG 기반 동화 생성**: Vector DB 도입으로 기존 동화 스타일 참조
- **Multi-Agent 구조**: Safety Agent, Recommendation Agent, Voice Agent 등 필요 시 분리
- **LangGraph 도입**: 장면 생성 → 안전성 검수 → 연령 검수 → 감정 태깅 등 복잡한 워크플로우가 필요할 때 도입
- **추천 엔진**: 아이 선택 패턴 기반 동화 추천
- **다국어 지원**: 영어, 중국어 등 다국어 TTS 및 동화 콘텐츠
- **구독 모델**: 무료 체험 + 유료 구독
- **소셜 기능**: 동화 완주 뱃지, 가족 공유 기능

---

*이 문서는 MVP 개발을 위한 기획서입니다. 버전: v1.1 | 수정 반영: 단일 Story Agent + ElevenLabs TTS Pipeline*
