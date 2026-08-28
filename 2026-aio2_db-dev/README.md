# Database Development 실습

Supabase(PostgreSQL)와 Redis를 활용해 데이터베이스의 기초부터 인증, 채팅 데이터 관리, 캐싱까지 단계적으로 학습하는 프로젝트입니다.

Supabase에서 관계형 데이터를 설계하고 Python으로 CRUD를 수행한 뒤, FastAPI 채팅 서비스에 Auth와 RLS(Row Level Security)를 적용합니다. 마지막으로 Redis의 자료구조와 TTL을 익히고 세션 및 대화 이력에 Cache-Aside 패턴을 적용합니다.

> 이 저장소는 교육용 실습 프로젝트입니다. 일부 파일에는 직접 구현하거나 개선할 `TODO`와 연습문제가 남아 있으며, 운영 환경에서 바로 사용할 수 있는 완성형 서비스는 아닙니다.

## 학습 내용

- PostgreSQL 테이블, 기본키·외래키, 제약조건과 JOIN
- Supabase Python SDK를 이용한 CRUD
- 데이터 정규화, ERD와 컬럼 정의서
- FastAPI와 Supabase 연동
- Supabase Auth 기반 회원가입·로그인과 Bearer Token 인증
- 프로필 자동 생성 Trigger와 사용자별 접근을 제한하는 RLS Policy
- 대화 및 메시지 API 설계
- Redis String, Hash, List, Set, Sorted Set
- TTL, 세션 캐싱, Cache-Aside와 캐시 무효화
- Redis 장애 시 원본 데이터베이스로 우회하는 처리

## 기술 스택

- Python 3.11+
- Supabase / PostgreSQL
- Redis
- FastAPI / Uvicorn
- Pydantic
- Jupyter Notebook
- uv

## 프로젝트 구조

```text
2026-aio2_db-dev/
├── 1_supabase-basic-test/
│   ├── docs/                     # Supabase·FastAPI·Auth·Redis 상세 실습 문서
│   ├── sql/create_users.sql      # Supabase 기초 테이블 생성 SQL
│   ├── supabase-client.ipynb     # Supabase Python SDK CRUD 실습
│   ├── db.py                     # Supabase 관리자 클라이언트
│   └── pyproject.toml
├── 2_chat_service/
│   ├── sql/                      # 채팅 DB, Trigger, RLS 생성 SQL
│   └── backend/
│       ├── app/                  # FastAPI 애플리케이션
│       ├── .env.example
│       └── pyproject.toml
├── 3_redis-basic-test/
│   ├── 00_explore.ipynb          # Redis 탐색
│   ├── 01_datastructures.ipynb   # Redis 자료구조
│   ├── 02_ttl.ipynb              # TTL과 만료
│   ├── 03_cache_aside.ipynb      # Cache-Aside 패턴
│   ├── 04_session.ipynb          # 로그인 세션 캐싱
│   ├── 05_chat_history.ipynb     # 대화 이력 저장
│   ├── db.py / redis_client.py
│   └── .env.example
└── exam.excalidraw               # 실습 관련 다이어그램
```

각 하위 폴더는 독립된 `pyproject.toml`과 `uv.lock`을 가진 별도 Python 프로젝트입니다. 실습할 폴더로 이동한 뒤 각각 `uv sync`를 실행해야 합니다.

## 권장 학습 순서

### 1. Supabase 기초

`1_supabase-basic-test/docs`의 문서와 노트북을 다음 순서로 진행합니다.

1. `Supabase 시작.md`
2. `supabase-client.ipynb`
3. `부록_데이터베이스 설계 심화.md` (선택)
4. `FastAPI_Supabase 연동.md`
5. `Supabase Auth.md`
6. `Supabase_Redis 연동.md`

### 2. 채팅 서비스

Supabase SQL Editor에서 아래 파일을 번호 순서대로 실행합니다.

1. `2_chat_service/sql/1.create_table.sql`
2. `2_chat_service/sql/2_profile_trigger.sql`
3. `2_chat_service/sql/3_policy_create.sql`

SQL은 다음 요소를 생성합니다.

- `profiles`, `conversations`, `messages` 테이블
- 신규 Auth 사용자 가입 시 프로필을 자동 생성하는 Trigger
- 사용자 본인의 프로필·대화·메시지만 접근하도록 제한하는 RLS Policy
- 대화와 메시지 조회를 위한 인덱스

이후 `2_chat_service/backend`에서 FastAPI 앱을 실행하고 Swagger UI로 API를 실습합니다.

### 3. Redis 기초와 캐싱

`3_redis-basic-test`의 노트북을 `00`부터 `05`까지 순서대로 실행합니다. Redis 자료구조와 TTL을 먼저 익힌 뒤, 세션과 대화 이력에 캐시를 적용합니다.

## 환경 설정

### 1. Supabase 프로젝트 준비

Supabase 프로젝트를 만든 뒤 Project URL과 API Key를 확인합니다. 다음 값이 필요합니다.

- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_SERVICE_ROLE_KEY`: 서버 전용 관리자 키
- `SUPABASE_ANON_KEY`: 사용자 인증 및 RLS 요청에 사용하는 공개 키

`SERVICE_ROLE_KEY`는 RLS를 우회할 수 있는 민감한 서버 키입니다. 브라우저나 클라이언트 코드에 넣지 말고 외부에 공개하지 마세요.

### 2. Redis 준비

접속할 Redis 인스턴스를 준비하고 다음 값을 확인합니다.

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`

### 3. `.env` 생성

실습할 하위 프로젝트에 `.env` 파일을 만듭니다. 채팅 서비스는 다음과 같이 설정합니다.

```powershell
cd 2026-aio2_db-dev\2_chat_service\backend
Copy-Item .env.example .env
```

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
```

현재 채팅 서비스의 `.env.example`에는 `SUPABASE_ANON_KEY` 항목이 없지만 `app/db.py`에서 사용하므로 `.env`에 직접 추가해야 합니다.

Supabase 기초 프로젝트에는 `SUPABASE_URL`과 `SUPABASE_SERVICE_ROLE_KEY`가 필요합니다. Redis 노트북 프로젝트에는 해당 두 값과 Redis 접속 정보가 필요합니다.

## 설치 및 실행

### Supabase 기초 실습

```powershell
cd 2026-aio2_db-dev\1_supabase-basic-test
uv sync
```

VS Code 등 Jupyter Notebook을 지원하는 편집기에서 `supabase-client.ipynb`를 열고 이 프로젝트의 `.venv`를 커널로 선택합니다.

### FastAPI 채팅 서비스

```powershell
cd 2026-aio2_db-dev\2_chat_service\backend
uv sync
uv run uvicorn app.main:app --reload
```

서버 실행 후 다음 주소에서 확인할 수 있습니다.

- 상태 확인: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

### Redis 노트북 실습

```powershell
cd 2026-aio2_db-dev\3_redis-basic-test
Copy-Item .env.example .env
uv sync
```

`00_explore.ipynb`부터 순서대로 열고 해당 프로젝트의 `.venv`를 커널로 선택합니다.

## 주요 API

| 메서드 | 경로 | 설명 | 인증 |
| --- | --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 | 불필요 |
| `POST` | `/auth/signup` | 이메일과 비밀번호로 회원가입 | 불필요 |
| `POST` | `/auth/login` | 로그인 및 Access Token 발급 | 불필요 |
| `GET` | `/me` | 현재 로그인 사용자 확인 | Bearer Token |
| `GET` | `/me/profile` | 내 프로필 조회 | Bearer Token |
| `PATCH` | `/me/profile` | 내 사용자 이름 수정 | Bearer Token |
| `GET` | `/me/conversations` | 내 대화 목록 조회 | Bearer Token |
| `POST` | `/conversations` | 대화 생성 | 현재 구현은 관리자 클라이언트 사용 |
| `GET` | `/conversations?user_id={uuid}` | 사용자별 대화 목록 | 현재 구현은 관리자 클라이언트 사용 |
| `POST` | `/conversations/{id}/messages` | 메시지 저장 및 캐시 무효화 | 현재 구현은 관리자 클라이언트 사용 |
| `GET` | `/conversations/{id}/messages` | 메시지 목록 조회 및 캐싱 | 현재 구현은 관리자 클라이언트 사용 |

Swagger UI에서 인증 API로 로그인한 뒤 응답의 `access_token`을 복사하고, 우측 상단 **Authorize** 버튼에 입력하면 `/me` API를 호출할 수 있습니다.

## 데이터 흐름

```text
Client
  └─ HTTP 요청
      └─ FastAPI
          ├─ Supabase Auth: 회원가입, 로그인, 토큰 검증
          ├─ PostgreSQL: 프로필, 대화, 메시지 원본 저장
          └─ Redis: 세션과 메시지 목록의 임시 캐시
```

Redis 데이터는 원본이 아닌 사본입니다. 캐시 조회에 실패하면 PostgreSQL에서 데이터를 읽고, 새 메시지가 저장되면 기존 메시지 캐시를 삭제하는 Cache-Aside 방식으로 구성되어 있습니다.

## 현재 구현 상태와 주의 사항

- 여러 파일에 교육용 `TODO`, 주석 처리된 예제와 연습문제 코드가 남아 있습니다.
- 인증된 `/me` API는 사용자 토큰과 RLS를 사용하지만, `/conversations` API는 현재 `SERVICE_ROLE_KEY` 기반 관리자 클라이언트를 사용합니다.
- `measure.py`의 `TOKEN`과 `CONVERSATION_ID`는 실행 전에 본인의 임시 값으로 교체해야 합니다. 실제 Access Token은 소스 코드에 커밋하지 말고, 노출했다면 즉시 세션을 폐기하거나 키를 교체하세요.
- `.env`, Service Role Key, Redis 비밀번호와 Access Token을 Git에 커밋하지 마세요.
- 외부 Supabase 및 Redis 인스턴스가 필요하므로 연결 정보 없이 전체 통합 테스트를 실행할 수 없습니다.
- 운영 환경에서는 CORS, 비밀 관리, 세분화된 권한 검사, 로깅과 테스트를 별도로 보강해야 합니다.

## 자주 발생하는 오류

- **환경변수 관련 `KeyError`**: 명령을 실행한 폴더에 `.env`가 있는지, 필요한 변수명이 모두 있는지 확인합니다.
- **Supabase 인증 오류**: URL과 Anon/Service Role Key가 서로 같은 프로젝트의 값인지 확인합니다.
- **RLS 오류 또는 빈 결과**: SQL Policy를 적용했는지, 요청에 올바른 Bearer Token이 있는지 확인합니다.
- **Redis 연결 오류**: Host, Port, Password와 Redis 인스턴스의 실행 상태를 확인합니다.
- **`401 Unauthorized`**: Access Token이 만료되었거나 Swagger UI의 Authorize 설정이 빠졌는지 확인합니다.
- **`422 Unprocessable Entity`**: 요청 본문의 필드와 UUID 형식이 Pydantic 모델에 맞는지 확인합니다.
