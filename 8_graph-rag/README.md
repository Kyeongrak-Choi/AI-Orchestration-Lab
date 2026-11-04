# GraphRAG 특별교육 실습 자료

Neo4j 그래프 데이터베이스에 OpenAI API와 LangChain을 결합해 벡터 RAG, Text2Cypher, Vector + Graph 하이브리드 RAG를 만드는 실습 자료입니다.

| 자료 | 내용 |
|---|---|
| `[배포용] GraphRAG 실습 가이드.md` | 1~10장 실습 가이드. 노트북 셀의 "실습 가이드 7-3" 같은 번호가 이 문서의 절 번호입니다 |
| `2026-graph-rag/` | 실습 폴더. `c:\study\2026-graph-rag`로 복사해서 씁니다 |

## 시작하기

1. `2026-graph-rag` 폴더를 `c:\study\2026-graph-rag`로 복사합니다.
2. PowerShell에서 실행합니다.

    ```powershell
    cd c:\study\2026-graph-rag
    uv sync
    copy .env.example .env
    code .
    ```

3. `.env`에 OpenAI 키를 넣고, `notebooks\0_start.ipynb`에서 `API Key configured: True`를 확인합니다.
4. Neo4j 준비(샌드박스 또는 Docker)는 가이드 2장과 5-5를 따릅니다.

자세한 절차는 가이드 5장(실습 환경 준비)에 있습니다.

## 실습 폴더 구성

| 경로 | 내용 |
|---|---|
| `notebooks/ch04, ch06~ch09_*.ipynb` | 실습 노트북. 파일 이름의 숫자가 가이드의 장 번호입니다 |
| `notebooks/0_start.ipynb` | OpenAI 키 확인 |
| `tools/graphrag_tools.py` | 노트북에서 쓰는 연결·환경 확인 함수 |
| `docker/` | Docker로 Neo4j(Recommendations, POLE, 빈 DB)를 띄우는 설정 |
| `.env.example` | 접속 정보 견본. `.env`로 복사해 값을 채웁니다 |

> `.env`에는 OpenAI 키가 들어갑니다. 공유 폴더, 화면 공유, 메신저, 깃 저장소에 올리지 않습니다.
