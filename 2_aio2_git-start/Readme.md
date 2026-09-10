# example

added by visual code / added by Github web


change by vs code 1

change by vs code 2


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
