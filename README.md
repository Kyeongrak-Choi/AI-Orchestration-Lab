# [Encore]AI Orchestration lab

<details>
<summary>2026-git-start</summary>

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


<details>
<summary>2026_aio2_python-basic</summary>

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

<details>
<summary>2026_aio2_fastapi</summary>

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

<details>
<summary>2026-aio2_llm-api</summary>

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
2026-aio2_llm-api/
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
cd 2026-aio2_llm-api
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

<details>
<summary>2026-aio2_db-dev/sql</summary>

기본 SQL 문법 연습 프로젝트
    
</details>
<details>
<summary>Coming soon</summary>

</details>

