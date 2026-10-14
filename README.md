# [Encore]AI Orchestration lab

> AI 오케스트레이션 과정에서 진행한 실습과 프로젝트를 한곳에 정리한 학습 기록입니다.

## Projects

- [📖 Git Collaboration](#git-collaboration)
- [🐍 Python Basic](#python-basic)
- [⚡ FastAPI Basic](#fastapi-basic)
- [🤖 LLM API](#llm-api)
- [🗄 Database Development](#database-development)
- [🧠 LLM Application Development](#llm-application-development)
- [🎨 UI / UX Practice](#ui-ux-practice)
- [🚀 Agent Development](#agent-development)

---

<a id="git-collaboration"></a>

<details>
<summary><strong>📖 Git Collaboration (git-start)</strong></summary>

-------------------------

# Git 협업 실습: Fetch, Merge 및 충돌 해결

작업자 A와 작업자 B가 하나의 GitHub 원격 저장소를 각자의 로컬 저장소로 복제한 뒤, 같은 파일을 수정하면서 발생하는 Push 거절과 Merge Conflict를 해결하는 과정을 나타낸다.

## 전체 시퀀스 다이어그램

```mermaid
sequenceDiagram
    autonumber
    participant A as 작업자 A의 로컬 저장소
    participant G as GitHub 원격 저장소<br/>origin/main
    participant B as 작업자 B의 로컬 저장소

    rect rgb(235, 245, 255)
        Note over A,B: 1. 독립적인 로컬 저장소 준비
        A->>G: git clone 저장소_URL
        G-->>A: main 브랜치 복제
        B->>G: git clone 저장소_URL
        G-->>B: main 브랜치 복제
        Note over A: A의 로컬 저장소와 작업 공간
        Note over B: B의 로컬 저장소와 작업 공간
    end

    rect rgb(235, 255, 240)
        Note over A,G: 2. 작업자 A가 먼저 변경 사항 게시
        A->>A: README.md 수정
        A->>A: git add README.md
        A->>A: git commit -m "A의 변경 사항"
        A->>G: git push origin main
        G-->>A: Push 성공
        Note over G,B: 원격 main에는 A의 Commit이 있지만<br/>B의 로컬 main에는 아직 반영되지 않음
    end

    rect rgb(255, 245, 230)
        Note over B,G: 3. 작업자 B의 Push가 거절됨
        B->>B: README.md의 같은 부분 수정
        B->>B: git add README.md
        B->>B: git commit -m "B의 변경 사항"
        B->>G: git push origin main
        G--xB: Push rejected - fetch first
        Note over B,G: 원격 저장소에 B가 갖고 있지 않은<br/>A의 Commit이 있으므로 Push 불가
    end

    rect rgb(255, 235, 235)
        Note over B,G: 4. Fetch 및 Merge 수행
        B->>G: git fetch origin
        G-->>B: 최신 origin/main과 A의 Commit 전달
        Note over B: fetch는 원격 추적 브랜치만 갱신하며<br/>로컬 main을 자동으로 변경하지 않음
        B->>B: git merge origin/main

        alt README.md의 같은 부분이 수정된 경우
            B--xB: Merge Conflict 발생
            Note over B: 충돌 표시를 확인하고<br/>A와 B의 내용을 올바르게 통합
            B->>B: README.md 충돌 해결 및 저장
            B->>B: git add README.md
            B->>B: git commit -m "Merge conflict 해결"
        else 수정 위치가 겹치지 않은 경우
            B->>B: 자동 Merge 완료
        end
    end

    rect rgb(240, 235, 255)
        Note over B,G: 5. 해결 결과를 원격 저장소에 반영
        B->>G: git push origin main
        G-->>B: Push 성공
        Note over G: origin/main에 A와 B의 변경 사항이 모두 반영됨
    end

    rect rgb(235, 250, 250)
        Note over A,G: 6. 작업자 A의 최종 동기화
        A->>G: git fetch origin
        G-->>A: B의 Merge Commit 전달
        A->>A: git merge origin/main
        Note over A,B: 두 작업자의 로컬 main과<br/>GitHub origin/main이 최종 동기화됨
    end
```

## 핵심 정리

- 작업자 A와 B의 로컬 저장소는 서로 독립적이다.
- 다른 작업자가 Push한 내용은 내 로컬 저장소에 자동으로 반영되지 않는다.
- `git fetch origin`은 원격 변경 사항을 가져와 `origin/main`을 갱신한다.
- `git merge origin/main`은 가져온 변경 사항을 현재 로컬 브랜치에 병합한다.
- 같은 파일의 같은 부분을 수정하면 Merge Conflict가 발생할 수 있다.
- 충돌을 직접 수정한 뒤 `add`, `commit`, `push` 순서로 해결 결과를 게시한다.

## 충돌 해결 명령어 요약

```bash
git fetch origin
git merge origin/main

# README.md의 충돌 부분을 직접 수정한 뒤 실행
git add README.md
git commit -m "Merge conflict 해결"
git push origin main
```

</details>


<br />

<a id="python-basic"></a>

<details>
<summary><strong>🐍 Python Basic (python-basic)</strong></summary>

# 🐍 Python Basic

A repository for learning Python fundamentals, from basic syntax to object-oriented programming.

## 📚 Topics

- Python Basics
- Functions
- Modules & Packages
- Object-Oriented Programming (OOP)
- Exception Handling
- Collections

## 🛠 Tech Stack

- Python 3.13+
- VS Code
- Jupyter Notebook
- Git & GitHub
- pip
- Ruff https://pypi.org/project/ruff/

## 🎯 Goal

- Understand Python fundamentals
- Write clean and Pythonic code
- Build a strong foundation in object-oriented programming
- Develop practical coding skills through hands-on practice

</details>

<br />

<a id="fastapi-basic"></a>

<details>
<summary><strong>⚡ FastAPI Basic (fastapi)</strong></summary>

  # 📚 FastAPI Basic

FastAPI와 Pydantic을 활용하여 **도서 관리 API**를 구현하는 학습 프로젝트입니다.

도서 조회, 검색, 등록 기능을 구현하며 REST API의 기본 개념을 익히고, 정적 HTML 페이지를 통해 API를 직접 테스트할 수 있습니다.

---

## 🚀 Features

- 도서 목록 조회
- 도서 상세 조회
- 제목 검색
- 저자별 필터 및 연도 정렬
- 페이지네이션
- 도서 등록
- Swagger / ReDoc API 문서 제공

---

## 🛠 Tech Stack

- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn

---

## ▶️ Getting Started

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install fastapi "uvicorn[standard]"

uvicorn main:app --reload
```

서버 실행 후 아래 주소에서 확인할 수 있습니다.

| 페이지 | 주소 |
| ------ | ---- |
| Practice | http://127.0.0.1:8000/static/index.html |
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 📌 API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/health` | 서버 상태 확인 |
| GET | `/info` | API 정보 조회 |
| GET | `/books` | 도서 목록 조회 |
| GET | `/books/{book_id}` | 도서 상세 조회 |
| GET | `/books/search?keyword=...` | 제목 검색 |
| GET | `/books/filter?author=...&sort=year` | 저자 필터 및 정렬 |
| GET | `/books/page?skip=0&limit=2` | 페이지 조회 |
| POST | `/books` | 도서 등록 |

---

## 📝 Sample Request

```json
{
  "title": "FastAPI 시작하기",
  "author": "홍길동",
  "year": 2026,
  "tags": [
    "Python",
    "API"
  ],
  "publisher": {
    "name": "예제 출판사",
    "city": "Seoul"
  }
}
```

> **Note**
>
> 현재 데이터는 메모리(In-Memory)에 저장되므로 서버를 재시작하면 초기화됩니다.

---

## 📂 Project Structure

```text
.
├── main.py              # FastAPI 애플리케이션 및 API
├── hello.py             # FastAPI 기본 예제
├── test.ipynb           # 학습용 노트북
└── static/
    └── index.html       # API 테스트 페이지
```

---

## 🎯 Learning Goals

- FastAPI 기본 사용법 이해
- Pydantic을 이용한 데이터 검증
- REST API 설계 및 구현
- Query Parameter와 Path Parameter 활용
- Swagger/OpenAPI 문서 활용

</details>

<br />

<a id="llm-api"></a>

<details>
<summary><strong>🤖 LLM API (llm-api)</strong></summary>

# LLM API 기초 실습

Gemini와 OpenAI API를 직접 호출하며 LLM 애플리케이션의 기본 개념을 익히는 실습 프로젝트입니다. 첫 API 호출부터 토큰과 비용, 생성 파라미터, 멀티턴 대화까지 단계적으로 학습하고, 마지막에는 Gemini 호출을 FastAPI 엔드포인트로 감쌉니다.

> 이 저장소는 학습용 골격입니다. 노트북과 `app.py`의 `TODO`를 직접 구현하며 완성하는 방식으로 구성되어 있습니다.

## 학습 내용

- Gemini/OpenAI SDK로 LLM 호출하기
- 응답 객체와 토큰 사용량 확인하기
- 토큰 수를 바탕으로 API 비용 계산하기
- `temperature`, `top_p`, `max_output_tokens` 등 생성 파라미터 비교하기
- 싱글턴 호출과 멀티턴 대화의 차이 이해하기
- 대화 이력 증가에 따른 비용과 슬라이딩 윈도우 적용하기
- LLM 호출을 FastAPI API로 제공하기
- 외부 API 오류를 적절한 HTTP 오류로 변환하기

## 기술 스택

- Python 3.11+
- Google Gen AI SDK (`google-genai`)
- OpenAI Python SDK (`openai`)
- FastAPI / Uvicorn
- Pydantic
- Jupyter Notebook / IPykernel
- uv

## 프로젝트 구조

```text
4_llm-api/
├── notebooks/
│   ├── 01_first_call.ipynb          # 첫 호출, 응답 구조, 시스템 지침, 오류 처리
│   ├── 02_tokens_and_cost.ipynb     # 토큰 계산, 과금, 사용량 제한
│   ├── 03_parameters.ipynb          # 생성 파라미터와 비용 통제
│   ├── 04_single_vs_multiturn.ipynb # 대화 이력, 세션 API, 슬라이딩 윈도우
│   └── 05_fastapi_integration.ipynb # FastAPI 연동 실습
├── app.py                            # Gemini 기반 FastAPI 실습 골격
├── pyproject.toml                    # 프로젝트 및 의존성 정의
├── requirements.txt                 # pip용 고정 의존성 목록
└── uv.lock                           # uv 잠금 파일
```

## 시작하기

### 1. 프로젝트 디렉터리로 이동

```powershell
cd 4_llm-api
```

### 2. 의존성 설치

이 프로젝트는 `uv` 사용을 권장합니다.

```powershell
uv sync
```

`pip`을 사용한다면 다음과 같이 설치할 수 있습니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. API 키 설정

프로젝트 루트에 `.env` 파일을 만들고 사용할 API 키를 입력합니다.

```dotenv
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

- Gemini는 전체 실습과 FastAPI 앱에서 사용합니다.
- OpenAI는 두 SDK를 비교하는 노트북 실습에서 사용합니다.
- OpenAI API 호출에는 별도 사용 요금이 발생할 수 있습니다.
- `.env`는 Git에서 제외되어 있습니다. API 키를 코드, 노트북 출력 또는 커밋에 포함하지 마세요.

### 4. 노트북 실행

VS Code 등 Jupyter Notebook을 지원하는 편집기에서 `notebooks/01_first_call.ipynb`를 열고, 프로젝트의 `.venv`를 커널로 선택합니다. 노트북은 번호 순서대로 진행하는 것을 권장합니다.

각 노트북은 설명과 참고 코드 다음에 직접 작성할 `TODO` 셀을 제공합니다. API를 실제로 호출하므로 반복 실행 시 사용량 제한이나 비용에 유의하세요.

## FastAPI 앱 실행

`app.py`는 노트북 05의 내용을 독립 실행 가능한 API로 옮긴 실습 골격입니다.

```powershell
uv run uvicorn app:app --reload
```

서버가 실행되면 다음 주소를 사용할 수 있습니다.

- Swagger UI: <http://127.0.0.1:8000/docs>
- 상태 확인: <http://127.0.0.1:8000/health>

### API 엔드포인트

#### `GET /health`

서버 상태, 사용 모델, Gemini API 키 로드 여부를 확인합니다. 키 값 자체는 반환하지 않습니다.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

#### `POST /ask`

질문을 Gemini에 전달하고 답변과 토큰 사용량을 반환합니다.

```powershell
$body = @{ question = "FastAPI를 한 문장으로 설명해줘" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/ask `
  -ContentType "application/json" `
  -Body $body
```

요청 형식:

```json
{
  "question": "FastAPI를 한 문장으로 설명해줘"
}
```

`question`은 1자 이상 500자 이하만 허용됩니다.

## 현재 FastAPI 실습 과제

현재 `app.py`에는 다음 작업이 `TODO`로 남아 있습니다.

- 요청 모델에 `temperature`, `max_output_tokens`, `system_instruction` 추가
- 요청 파라미터를 Gemini 생성 설정에 전달
- Gemini의 토큰 사용량을 API 응답 모델에 매핑
- `429`, `503` 등 일시적 외부 API 오류를 HTTP `503`으로 변환

따라서 과제를 완료하기 전 `/ask`의 토큰 사용량은 모두 `0`으로 반환되며, 생성 옵션도 아직 요청으로 받을 수 없습니다.

## 사용 모델

코드에 설정된 기본 모델은 다음과 같습니다.

- Gemini: `gemini-3.1-flash-lite`
- OpenAI: `gpt-4o-mini`

모델을 사용할 수 없다는 오류가 발생하면 계정과 API 키에서 접근 가능한 모델인지 확인한 뒤, 각 노트북의 `MODEL` 또는 `OA_MODEL` 값을 변경하세요.

## 문제 해결

- **API 키를 찾지 못하는 경우**: `.env`가 프로젝트 루트에 있는지, 변수 이름에 오타가 없는지 확인합니다.
- **인증 오류가 계속되는 경우**: `.env`를 수정한 뒤 노트북 커널이나 Uvicorn 서버를 다시 시작합니다.
- **모델을 찾을 수 없는 경우**: 해당 API 키에서 이용 가능한 모델로 모델명을 변경합니다.
- **`429` 오류가 발생하는 경우**: 호출 한도를 초과한 상태이므로 잠시 기다린 뒤 재시도합니다.
- **`422` 오류가 발생하는 경우**: `/ask` 요청 본문과 `question` 길이 제한을 확인합니다.

## 주의 사항

- LLM의 응답은 매번 달라질 수 있으며 사실과 다른 내용을 포함할 수 있습니다.
- 토큰 단가와 무료 사용 한도는 변경될 수 있으므로 비용 계산 실습 시 각 제공사의 최신 정책을 확인하세요.
- 이 앱에는 인증, 데이터베이스, 대화 이력 저장, 운영 환경용 보안 설정이 포함되어 있지 않습니다.

</details>

<br />

<a id="database-development"></a>

<details>
<summary><strong>🗄 Database Development (db-dev)</strong></summary>

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
5_db-dev/
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
cd 5_db-dev\2_chat_service\backend
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
cd 5_db-dev\1_supabase-basic-test
uv sync
```

VS Code 등 Jupyter Notebook을 지원하는 편집기에서 `supabase-client.ipynb`를 열고 이 프로젝트의 `.venv`를 커널로 선택합니다.

### FastAPI 채팅 서비스

```powershell
cd 5_db-dev\2_chat_service\backend
uv sync
uv run uvicorn app.main:app --reload
```

서버 실행 후 다음 주소에서 확인할 수 있습니다.

- 상태 확인: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

### Redis 노트북 실습

```powershell
cd 5_db-dev\3_redis-basic-test
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

    
</details>

<br />

<a id="llm-application-development"></a>

<details>
<summary><strong>🧠 LLM Application Development (llm-app-dev)</strong></summary>

# LLM Application Development 실습

OpenAI API와 LangChain 생태계를 활용해 **프롬프트 설계부터 도구 에이전트, MCP, RAG, 메모리, LangGraph 워크플로, 실행 추적까지** 단계적으로 구현하는 LLM 애플리케이션 개발 실습입니다.

단순히 모델의 답변을 출력하는 데서 끝나지 않고, 구조화된 출력·입출력 검증·프롬프트 인젝션 방어·외부 도구 연결·문서 검색·품질 평가·상태 저장을 조합해 실제 서비스에 가까운 흐름을 구성합니다.

> 노트북에는 개념 설명, 오류 재현, 비교 실험, 학습자용 TODO 셀이 함께 포함되어 있습니다. 실행 결과와 호출 비용은 모델·데이터·외부 서비스 상태에 따라 달라질 수 있습니다.

## 학습 로드맵

| 모듈 | 범위 | 주요 내용 |
| --- | --- | --- |
| M1. 프롬프트와 안전성 | Day00~Day04 | Zero-shot/Few-shot, CoT, 역할 프롬프트, ChatPromptTemplate, LCEL, Pydantic 구조화 출력, Prompt Injection 방어 |
| M2. 도구와 에이전트 | Day05~Day09 | Function Calling, LangChain Tool, 외부 API·스크래핑, MCP, `create_agent`, ReAct, 멀티툴 의사결정과 실패 대응 |
| M3. 지식과 기억 | Day10~Day13 | 임베딩·코사인 유사도, Chroma, PostgreSQL/pgvector, 세션 메모리, PDF 전처리, 질의 개선, 하이브리드 검색·리랭킹·RAG 평가 |
| M4. 워크플로와 통합 | Day14~Day17 | LangGraph State/Node/Edge, 조건 분기·반복·병렬 처리, Hybrid Memory, 체크포인트, Self-Reflection, Planning·Tracing 통합 |

## 주요 학습 내용

- **프롬프트 엔지니어링**: Zero-shot, Few-shot, 역할 지정, 출력 형식 제어, 재사용 가능한 프롬프트 팩토리
- **LCEL과 체인**: `ChatPromptTemplate | ChatOpenAI | StrOutputParser` 구성, 변수 바인딩, 배치 실행, 오류 확인
- **신뢰할 수 있는 출력**: Pydantic 모델·Enum·중첩 모델·필드 검증을 이용한 Structured Output
- **안전한 LLM 호출**: 입력 위험 패턴 차단, 외부 문서의 간접 인젝션 대응, 출력 검증과 민감한 시스템 지시 보호
- **Function Calling과 Tool**: 모델의 `tool_calls`를 해석하고 도구를 실행한 뒤 `ToolMessage`로 결과를 되돌리는 전체 루프
- **MCP와 에이전트**: stdio MCP 서버에서 도구를 검색하고, Function Calling과 MCP의 구조적 차이를 비교하며 여러 도구를 사용하는 에이전트 구현
- **브라우저 자동화와 외부 데이터**: Playwright, BeautifulSoup, `yfinance`, 뉴스·환율·금 시세 등 외부 데이터 도구 연결
- **임베딩과 Vector DB**: `text-embedding-3-small`, 코사인 유사도, Chroma 로컬 저장소, PostgreSQL `pgvector` 검색
- **RAG 고도화**: 문서 청킹, PDF→Markdown 변환, Query Rewriting, HyDE, Multi-Query, RAG Fusion, BM25+의미 검색, FlashRank 재순위
- **RAG 평가**: Context Hit, Faithfulness, Answer Relevancy, Answer Correctness, Precision@5를 이용한 검색·생성 품질 비교
- **상태 기반 워크플로**: LangGraph의 StateGraph, 노드·엣지, 조건 분기, 루프, fan-out/fan-in, Planning·Executor·Replanner 패턴
- **메모리와 개선 루프**: 세션별 대화 기억, 장기 지식 검색, `MemorySaver`/`PostgresSaver`, 생성-비평-수정 Self-Reflection
- **관찰 가능성**: `.stream`으로 노드별 실행 흐름과 소요 시간을 확인하고, 선택적으로 LangSmith에서 프롬프트·토큰·실패 지점을 추적

## 기술 스택

- Python 3.11+
- `uv`, Jupyter Notebook / IPykernel
- OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)
- LangChain, LangGraph, LangChain MCP Adapters, Pydantic
- PostgreSQL / `pgvector`, Psycopg, SQLAlchemy
- ChromaDB, BM25, FlashRank
- PyMuPDF / PyMuPDF4LLM, BeautifulSoup, pandas, yfinance
- Playwright / Chromium
- 선택 사항: LangSmith

## 프로젝트 구조

```text
6_llm-app-dev/
├── notebooks/
│   ├── Day00~Day17 실습 노트북 및 MCP·Playwright 스크립트
│   ├── data/                    # RAG 실습용 PDF 문서
│   ├── html/sample.html         # 로컬 스크래핑 실습 대상
│   └── chroma_store/            # Chroma 로컬 영속 저장소
├── app.py                       # sample.html과 health를 제공하는 ASGI 앱
├── math_server.py               # 덧셈·곱셈 MCP 서버
├── review_server.py             # 회사 리뷰 MCP 서버
├── book_server.py               # SQLite 기반 도서 조회 MCP 서버
├── book_host_bot.py             # OpenAI 모델과 도서 MCP 서버를 연결하는 호스트
├── mcp_demo.py                  # MCP 도구 검색 데모
├── playwright_test_01.py        # 브라우저 실행 기본 예제
├── playwright_test_02.py        # quotes.toscrape.com 스크래핑 예제
├── pyproject.toml               # 의존성 및 프로젝트 설정
├── uv.lock                      # 의존성 잠금 파일
└── .env.example                 # 환경변수 예시
```

`my_database.db`, `notebooks/chroma_store/`, `flashrank_cache/`는 각각 도서 MCP·Chroma·FlashRank 실습에서 사용하는 로컬 데이터 또는 캐시입니다.

## 시작하기

### 1. 의존성 설치

```powershell
cd 6_llm-app-dev
uv sync
```

### 2. 환경변수 설정

```powershell
Copy-Item .env.example .env
```

`.env`에 최소한 OpenAI API 키를 입력합니다.

```dotenv
OPENAI_API_KEY=your_openai_api_key

# Day11 이후 PostgreSQL·pgvector·체크포인터 실습에 필요
DATABASE_URL=postgresql://user:password@host:5432/database

# Day11 확장 투자 리서치 실습에서 선택적으로 사용
OPENAI_MODEL=gpt-4o-mini

# Day17 부록 LangSmith 추적에서 선택적으로 사용
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=llm-dev-day17
```

Day12 이후 RAG 실습을 실행하려면 PostgreSQL에 `vector` 확장을 활성화해야 합니다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. 노트북 실행

VS Code 등 Jupyter를 지원하는 편집기에서 `notebooks`의 파일을 열고 `6_llm-app-dev/.venv`를 커널로 선택합니다. 기본적으로 아래 순서대로 진행합니다.

```text
Day00 → Day01 → Day02 → Day03 → Day04
      → Day05 → Day06 → Day07 → Day08 → Day09
      → Day10 → Day11 → Day12 → Day13-1~4
      → Day14 → Day15 → Day16 → Day17
      → Day17-부록-LangSmith추적 (선택)
```

Day11 확장 노트북은 기본 세션 메모리 실습을 먼저 진행한 뒤 실행하는 것을 권장합니다.

## 실행 예제

### 로컬 ASGI 페이지와 스크래핑

`app.py`는 `notebooks/html/sample.html`을 제공하는 간단한 ASGI 앱입니다.

```powershell
uv run uvicorn app:app --reload
```

이후 `http://127.0.0.1:8000/sample.html`을 열어 페이지를 확인할 수 있습니다. Playwright 예제를 실행하려면 최초 1회 Chromium을 설치합니다.

```powershell
uv run playwright install chromium
uv run python playwright_test_02.py
```

스크래핑 예제는 외부 사이트에 접속하므로 네트워크 상태와 대상 사이트의 정책에 영향을 받습니다.

### MCP 도구 호스트

MCP 서버는 stdio로 실행되는 별도 프로세스이며, 호스트 프로그램이 서버의 도구를 가져와 LLM에 바인딩합니다.

```powershell
uv run python mcp_demo.py
uv run python book_host_bot.py
```

`book_host_bot.py`는 `book_server.py`의 `get_book_by_rank`, `search_book` 도구를 연결해 도서 순위 조회와 제목·저자 검색을 수행합니다. `math_server.py`와 `review_server.py`는 Day07 Function Calling vs MCP 비교 실습에서 사용합니다.

Windows에서 MCP stdio를 사용하는 Day07·Day08 스크립트는 Jupyter 셀보다 터미널에서 `uv run python`으로 실행하는 것을 권장합니다.

## 최종 통합 프로젝트

Day17에서는 앞선 모듈의 결과를 하나의 모의면접 코치·리서치 도우미 흐름으로 통합합니다.

```text
사용자 질문
   │
   ▼
입력 방어 → 계획(Planning) → 지식 검색(pgvector) → 도구/LLM 답변
                                      │
                                      ▼
                               비평·품질 확인
                                  ├─ 부족: 수정 루프
                                  └─ 통과: 최종 답변·대화 기억 저장
```

- M1의 시스템 프롬프트와 입력·출력 방어
- M2의 도구 호출과 에이전트
- M3의 pgvector 지식 검색과 세션 기억
- M4의 LangGraph 분기·반복·체크포인트·Self-Reflection
- `.stream` 실행 로그와 LangSmith 선택적 추적

을 하나의 실행 흐름으로 연결해, LLM 애플리케이션을 구성 요소 단위로 설계하고 관찰하는 방법을 연습합니다.

## 주의 사항

- OpenAI API와 임베딩 호출에는 비용이 발생할 수 있으며, 반복 실행 시 사용량을 확인해야 합니다.
- `OPENAI_API_KEY`, `DATABASE_URL`, `LANGSMITH_API_KEY`와 같은 비밀값은 커밋하지 않습니다.
- Day11~Day13, Day15, Day17의 PostgreSQL·pgvector 실습은 외부 DB 연결이 필요합니다. 연결 정보가 없으면 해당 실습을 실행할 수 없습니다.
- Playwright·yfinance·뉴스/스크래핑 예제는 외부 네트워크와 대상 서비스의 응답에 의존합니다.
- LangSmith 추적은 선택 사항이며, 다른 노트북은 기본적으로 추적을 끄도록 구성되어 있습니다. 민감한 입력·출력은 추적 서비스로 보내지 않도록 주의합니다.
- 교육용 실습 코드이므로 인증, 비밀 관리, 요청 제한, 운영 로깅, 테스트와 같은 운영 환경 보강이 필요합니다.

</details>

<br />

<a id="ui-ux-practice"></a>

<details>
<summary><strong>🎨 UI / UX Practice</strong></summary>
    https://manus.im/
<p align="center">
    <img width="960" height="905" alt="image" src="https://github.com/user-attachments/assets/8954dd74-3c3c-44e6-8865-b94678bf0852" />
</p>

    

<details>
<summary><strong>🗂 IA</strong></summary>
   
```text
Home
├── Header
│   ├── Logo
│   ├── 기능
│   ├── 솔루션
│   ├── 자료
│   ├── 이벤트
│   ├── 팀
│   ├── 가격
│   ├── 로그인
│   └── 회원가입
│
├── Notice Banner
│   ├── 데이터 삭제 안내
│   └── 계정 복원하기
│
├── Main Section
│   ├── Hero Title
│   ├── AI Prompt Input
│   │   ├── 작업 입력
│   │   ├── 파일 첨부
│   │   └── 작업 전송
│   │
│   └── Quick Actions
│       ├── 슬라이드 제작
│       ├── 웹사이트 구축
│       ├── 디자인
│       ├── 게임 제작
│       └── 더보기
│
└── AI Workspace
     ├── 작업 생성
     ├── AI 처리
     └── 결과 확인

```
    
</details>

<details>
<summary><strong>👤 User Flow</strong></summary>
<p align="center">
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/960f9762-a70c-4d2b-a25b-489afc0efcf0" />
</p>


</details>

<details>
<summary><strong>🖥️ Wireframe</strong></summary>
<p align="center">
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/27f54358-6064-4202-a3d2-be4a756e65fc" />
</p>


</details>


</details>

<br />

<a id="agent-development"></a>

<details>
<summary><strong>🚀 Agent Development</strong></summary>

</details>

