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
<summary>Coming soon</summary>

</details>

