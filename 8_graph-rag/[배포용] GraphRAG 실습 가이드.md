---
title: GraphRAG 실습 가이드
course: 그래프 DB와 GraphRAG 구현
tags: [graphrag, neo4j, cypher, langchain, 실습가이드]
audience: 교육생
---

# GraphRAG 실습 가이드

Neo4j 그래프 데이터베이스에 OpenAI API와 LangChain을 결합해 벡터 RAG, Text2Cypher, Vector+Graph 하이브리드 RAG를 차례로 만든다. 원리가 중요한 단계는 OpenAI SDK로 직접 구현해 본 뒤 같은 기능을 LangChain 컴포넌트로 바꾼다.

> [!note] 이 가이드를 읽는 방법
> 실습 노트북 셀에 적힌 "실습 가이드 6-3" 같은 번호는 이 가이드의 절 번호다. 노트북을 실행하다가 설명이 필요하면 해당 절을 찾아 읽는다.

## 학습 목표

1. 관계형 DB와 그래프 DB의 차이를 설명하고, 그래프 DB가 RAG에 필요한 이유를 멀티홉 관점에서 말할 수 있다.
2. Cypher 기본 문법으로 그래프를 조회하고, Python에서 `Neo4jGraph`로 쿼리를 실행할 수 있다.
3. `LLMGraphTransformer`로 텍스트에서 지식 그래프를 만들고 `Neo4jVector`로 벡터 검색을 할 수 있다.
4. OpenAI API로 Text2Cypher를 직접 구현하고, 같은 기능을 `GraphCypherQAChain`으로 구성할 수 있다.
5. LCEL로 벡터 검색과 그래프 검색을 결합한 하이브리드 RAG 체인을 만들 수 있다.


> [!warning] 노트북마다 연결할 DB가 다르다
> 노트북을 열기 전에 .env의 `NEO4J_*` 네 줄을 그 노트북의 DB로 바꾸고, 노트북 상단의 `Restart`로 커널을 재시작한다. 바꾸는 방법은 5-5에 있다.

모든 노트북의 공통 흐름

1. 맨 위 셀에서 연결할 DB와 .env 설정을 확인한다.
2. 연결 셀을 실행한다. 출력된 레이블별 노드 수로 맞는 DB에 연결됐는지 확인한다.
3. 본문 셀을 위에서부터 순서대로 실행한다.
4. 맨 아래 "실습 과제"의 빈 셀(`# 과제 N: 여기에 작성합니다`)에 코드를 작성한다.

---

## 1. 그래프 DB 소개

### 1-1. 관계형 DB와 그래프 DB

| 구분       | 관계형 DB           | 그래프 DB                     |
| -------- | ---------------- | -------------------------- |
| 기본 단위    | 테이블(Row, Column) | 노드(Node), 관계(Relationship) |
| 관계 표현    | 외래키와 JOIN        | 관계가 독립된 데이터(1급 객체)         |
| 다대다(M:N) | 중간 테이블 필요        | 관계로 직접 연결                  |
| 속성 저장    | 행에 저장            | 노드와 관계 모두에 저장              |
| 구조 변경    | 스키마 변경 필요        | 노드·관계 추가로 확장               |
| 강점       | 트랜잭션, 정형 데이터 집계  | 추천, 소셜 네트워크, 지식 그래프, 경로 탐색 |

관계에도 속성을 붙일 수 있다. 예: `(사용자)-[:RATED {rating: 4.5}]->(영화)`

### 1-2. 그래프 DB를 쓰는 이유

1. 현실의 데이터는 개체와 관계로 이루어져 있고, 그래프는 이를 그대로 표현한다.
2. 여러 단계를 거치는 연결 탐색에서 JOIN을 반복하지 않아도 된다.
3. 새로운 관계 유형이 생겨도 스키마를 고치지 않고 추가할 수 있다.
4. "이 영화를 좋아한 사람이 좋아한 다른 영화" 같은 추천 로직을 쿼리 한 줄로 표현한다.
5. 벡터 검색은 의미가 비슷한 문서만 찾는다. 그래프는 문서 사이의 관계(인용, 저자, 주제)를 따라가 근거를 보강한다.

### 1-3. 멀티홉(Multi-hop)

노드에서 노드로 한 번 이동하는 것을 1-hop이라 한다. 멀티홉은 중간 노드를 여러 개 거쳐 목표 노드까지 탐색하는 방식이다.

| 예 | 1-hop | 2-hop | 3-hop |
|---|---|---|---|
| 소셜 | 내 친구 | 친구의 친구 | 친구의 친구의 친구 |
| 추천 | 사용자가 본 영화 | 그 영화를 본 다른 사용자 | 그 사용자가 본 다른 영화 |

일반적인 벡터 RAG는 질문과 비슷한 문서를 한 번 찾는 1-hop 검색이다. "아인슈타인의 제자가 쓴 논문은?"처럼 인물 → 제자 → 논문으로 2-hop 이상 이동해야 답할 수 있는 질문은 그래프 탐색으로 해결한다. hop 수가 늘수록 탐색 범위가 기하급수적으로 커지므로 조건과 인덱스로 범위를 제한한다.

```cypher
// Alice의 친구의 친구 (2-hop)
MATCH (u:User {name: "Alice"})-[:FRIEND]->()-[:FRIEND]->(fof)
RETURN fof
```

### 1-4. Cypher와 SQL

SQL은 조건에 맞는 행을 고르는 언어이고, Cypher는 노드에서 출발해 관계를 따라가는 패턴을 그리는 언어다.

`MATCH`를 SQL의 `SELECT`로 착각하기 쉽지만, `MATCH`는 `FROM`과 `JOIN`에 해당하고 `SELECT`에 해당하는 것은 `RETURN`이다.

| 역할 | SQL | Cypher |
|---|---|---|
| 어디서 무엇을 찾을지 | `FROM`, `JOIN ... ON` | `MATCH` 패턴 |
| 조건 | `WHERE` | `WHERE`, 또는 패턴 안의 `{ }` |
| 결과로 돌려줄 것 | `SELECT` | `RETURN` |
| 묶어서 집계 | `GROUP BY` | 따로 없다. `RETURN`에 집계 함수와 일반 값을 함께 쓰면 일반 값 기준으로 자동으로 묶인다 |
| 정렬, 개수 | `ORDER BY`, `LIMIT`, `OFFSET` | `ORDER BY`, `LIMIT`, `SKIP` |

"배우별 출연 영화 수"를 두 언어로 쓰면 차이가 드러난다.

```sql
SELECT p.name, COUNT(*) AS movies
FROM person p
JOIN acted_in a ON a.person_id = p.id
JOIN movie m    ON m.id = a.movie_id
GROUP BY p.name;
```

```cypher
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p.name, count(m) AS movies
```

SQL은 `SELECT`로 무엇을 보여 줄지부터 쓰고 연결은 `JOIN ... ON`의 키 비교로 표현한다. Cypher는 `MATCH`로 연결 모양을 먼저 그리고, 보여 줄 것은 마지막 `RETURN`에서 정한다.

### 1-5. 이 과정에서 만드는 세 가지 검색 방식

| 방식 | 검색 방법 | 강점 | 약점 | LangChain 구성 요소 | 장 |
|---|---|---|---|---|---|
| Vector RAG | 질문 임베딩과 청크 임베딩의 유사도 | 표현이 달라도 의미가 비슷하면 찾는다 | 개수, 목록, 집계 질문에 답할 수 없다. 관련 없는 질문에도 가장 비슷한 것을 항상 돌려준다 | `Neo4jVector`, retriever | 7 |
| Text2Cypher | LLM이 질문을 Cypher로 바꿔 실행 | 쿼리가 맞으면 집계, 조건, 멀티홉 질문에 DB가 정확한 값을 계산한다 | LLM이 쿼리를 잘못 만들면 오류 없이 틀린 답을 낸다 | `GraphCypherQAChain` | 8 |
| Vector + Graph | 벡터로 시작 노드를 찾고 Cypher로 주변 관계를 확장 | 의미 검색과 관계 정보를 함께 얻는다 | 확장할 관계를 `retrieval_query`로 미리 정해야 한다. 시작 노드를 잘못 찾으면 관계 정보도 엉뚱해진다 | `Neo4jVector(retrieval_query=...)`, LCEL | 9 |

Text2Cypher에서 DB가 계산한 값은 정확하지만, 그 계산을 지시하는 쿼리는 LLM이 만든다. 쿼리가 질문을 잘못 해석하면 정확한 계산으로 틀린 답을 낸다. 8장에서 실제로 확인한다.

### 1-6. RAG 프롬프트 구성

RAG 프롬프트는 네 부분으로 나눠 설계한다.

1. 컨텍스트: 벡터 DB나 그래프 DB에서 검색한 내용
2. 질문: 사용자의 원 질문
3. 지시사항: 문서 근거로만 답할 것, 모르면 모른다고 할 것, 한국어로 답할 것
4. 출력 형식: 표, 요약, 단계별 설명 등

컨텍스트 자리에 들어가는 내용은 검색 방식마다 다르다.

| 방식 | 컨텍스트에 들어가는 것 |
|---|---|
| Vector RAG | 질문과 비슷한 청크의 원문 |
| Text2Cypher | LLM이 만든 Cypher를 실행한 결과 행 |
| Vector + Graph | 질문과 비슷한 노드의 텍스트와 `retrieval_query`로 가져온 관계 정보 |

Text2Cypher는 LLM을 두 번 호출하고, 호출마다 프롬프트가 다르다. DB 스키마는 첫 번째 프롬프트에, 컨텍스트는 두 번째 프롬프트에 들어간다.

```
[프롬프트 1: 쿼리 생성]  스키마 + 예시 + 질문      → LLM → Cypher
                                                          ↓ Neo4j에서 실행
[프롬프트 2: 답변 생성]  결과 행(컨텍스트) + 질문   → LLM → 답변
```

| 구분 | 프롬프트 1: 쿼리 생성 | 프롬프트 2: 답변 생성 |
|---|---|---|
| 목적 | 질문을 Cypher로 바꾼다 | 쿼리 결과를 문장으로 바꾼다 |
| 들어가는 것 | 스키마, few-shot 예시, 질문 | 쿼리 결과(컨텍스트), 질문, 지시사항 |
| GraphCypherQAChain 옵션 | `cypher_prompt` | `qa_prompt` |

스키마를 빼면 LLM은 레이블과 속성을 추측해 그럴듯하지만 실행되지 않거나 빈 결과를 내는 쿼리를 만든다. 스키마가 너무 크면 프롬프트가 길어져 비용이 늘고 정확도가 떨어진다.

### 확인 질문

1. 영화 추천 데이터에서 "사용자가 영화에 준 별점"은 노드와 관계 중 어디에 저장하는 것이 자연스러운가?
2. "Tom Hanks와 함께 출연한 배우가 감독한 영화"는 몇 hop 질문인가?

---

## 2. Neo4j 샌드박스 설정

Neo4j Sandbox는 설치 없이 웹 브라우저에서 쓰는 무료 Neo4j다. 예제 데이터가 미리 들어 있는 DB를 만들 수 있다. 이 가이드에서 쓰는 샌드박스는 다음과 같다.

| 샌드박스 | 쓰는 곳 |
|---|---|
| Movies | 3장 (Browser만) |
| Recommendations | 4장 (`ch04`), 6장 (`ch06`), 9장 (`ch09`) |
| POLE | 8장 (`ch08`) |
| Blank Sandbox (빈 DB) | 7장 (`ch07`), 10장 종합 과제 |

Recommendations와 POLE은 강사가 Docker로 준비했다면 만들지 않아도 된다(5-5).

### 2-1. 샌드박스 만들기

1. https://sandbox.neo4j.com 에 Google 계정으로 로그인한다.
2. 데이터셋을 선택하고 Create를 누른다. 먼저 Movies를 만든다.
3. 다운로드 폴더에 credentials 파일(예: `Movies Sandbox Credentials.txt`)이 저장된다. 6장 이후 노트북의 .env에 이 파일의 값을 쓰므로 위치를 기억해 둔다.

| credentials 파일 항목 | .env에 넣을 곳 |
|---|---|
| Bolt URL (`bolt://IP:7687`) | `NEO4J_URI` |
| Username | `NEO4J_USERNAME` |
| Password | `NEO4J_PASSWORD` |
| (없음) | `NEO4J_DATABASE=neo4j` |

> [!note] 샌드박스는 3일 뒤 사라진다
> 생성 후 3일이 지나면 샌드박스가 삭제된다. 사라지면 새로 만들고 credentials 파일 값을 .env에 다시 넣는다.

### 2-2. Neo4j Browser 접속

1. 샌드박스 카드에서 Open을 누르면 Connect to instance 화면이 나온다.
2. Connect with SSO가 켜진 상태에서 Connect with Sandbox Login을 누른다. 또는 Database user와 Password에 credentials 파일의 값을 넣고 Connect를 누른다.
3. 화면 위쪽에 보이는 `neo4j+s://긴문자열` 주소는 브라우저 전용이다. 노트북의 .env에는 credentials 파일의 `bolt://` 주소를 쓴다.
4. Query 화면 위쪽 입력창에 쿼리를 **하나씩** 입력하고 Ctrl+Enter로 실행한다. 여러 쿼리를 한꺼번에 실행하면 오류가 난다.

---

## 3. Movies 데이터베이스 탐색

Movies 샌드박스의 Neo4j Browser에서 그래프와 Cypher를 익힌다. 같은 쿼리를 Python에서 실행하는 것은 6장에서 한다.

### 3-1. Movies 데이터 탐색

2-2의 방법으로 Movies 샌드박스에 접속해 아래 쿼리를 하나씩 실행한다.

```cypher
CALL db.schema.visualization
```

```cypher
MATCH (n:Movie) RETURN n LIMIT 25
```

```cypher
MATCH (n:Movie {title: "Speed Racer"}) RETURN n
```

```cypher
MATCH (n1)-[r]->(n2) RETURN n1, r, n2 LIMIT 50
```

확인할 것

- 레이블은 Movie, Person 두 개이고 노드는 171개다.
- Person과 Movie 사이에 ACTED_IN, DIRECTED, PRODUCED, WROTE, REVIEWED 관계가 있고, Person 사이에 FOLLOWS 관계가 있다. 관계는 모두 253개다.
- 결과 화면의 Graph 탭과 Table 탭을 바꿔 가며 비교한다.

### 3-2. 쿼리 문법 이해

Cypher는 그래프 모양을 글자로 그리는 언어다. 기호 네 가지로 패턴을 만든다. SQL과의 대응은 1-4에 있다.

| 기호 | 의미 | 예 |
|---|---|---|
| `( )` | 노드 | `(n:Movie)` |
| `[ ]` | 관계 | `[r:ACTED_IN]` |
| `{ }` | 속성 | `{title: "Speed Racer"}` |
| `->`, `<-` | 관계의 방향 | `(p)-[:ACTED_IN]->(m)` |

#### `CALL db.schema.visualization`

| 부분 | 의미 |
|---|---|
| `CALL` | 프로시저(DB에 미리 만들어진 함수)를 실행한다 |
| `db.schema.visualization` | DB 구조를 그림으로 돌려주는 프로시저 |

데이터가 아니라 데이터의 설계도를 보여 준다. 레이블마다 노드 하나, 관계 유형마다 화살표 하나로 그린다. 처음 보는 DB에서 가장 먼저 실행하는 쿼리다.

CALL 문법

```
CALL 프로시저이름(인자1, 인자2, ...) YIELD 출력컬럼1, 출력컬럼2
[WHERE 조건]
RETURN ...
```

| 부분 | 의미 |
|---|---|
| 프로시저 이름 | 점(.)으로 구분한 이름. `db.*` DB 정보, `dbms.*` 서버 정보, `apoc.*` 확장 라이브러리 |
| `(인자)` | 프로시저에 넘기는 값. 인자가 없으면 `()` |
| `YIELD` | 프로시저가 돌려주는 컬럼 중 사용할 것을 고른다 |
| `WHERE`, `RETURN` | `YIELD` 뒤로는 일반 쿼리처럼 쓴다 |

```cypher
// 레이블 목록
CALL db.labels()
```

```cypher
// 관계 유형 목록
CALL db.relationshipTypes()
```

```cypher
// YIELD로 컬럼을 받아 정렬
CALL db.labels() YIELD label
RETURN label ORDER BY label
```

9장의 벡터 검색도 내부에서 `CALL db.index.vector.queryNodes('moviePlotIndex', 5, $embedding) YIELD node, score`를 실행한다. 9장 `retrieval_query`에서 쓰는 `node`와 `score`가 이 `YIELD`에서 나온 이름이다.

APOC

`apoc.*`로 시작하는 프로시저는 APOC라는 확장 라이브러리에 들어 있다. 6장 이후 쓰는 LangChain `Neo4jGraph`는 연결할 때 APOC로 스키마를 읽으므로, APOC가 없는 DB에서는 `Could not use APOC procedures` 오류가 난다. Sandbox, AuraDB, 실습용 Docker 이미지에는 모두 들어 있다.

```cypher
// DB 구조(레이블, 속성, 관계)를 한 번에 조회
CALL apoc.meta.schema()
```

#### `MATCH (n:Movie) RETURN n LIMIT 25`

| 부분 | 의미 |
|---|---|
| `MATCH` | 패턴에 맞는 데이터를 찾는다 |
| `n` | 찾은 노드에 붙이는 변수. 이름은 자유롭게 정한다 |
| `:Movie` | 레이블. Movie 노드만 찾는다 |
| `RETURN n` | 찾은 노드를 결과로 돌려준다 |
| `LIMIT 25` | 최대 25개만 돌려준다 |

노드 전체 대신 속성만 돌려주면 Table 탭에서 보기 좋다.

```cypher
MATCH (m:Movie) RETURN m.title, m.released LIMIT 25
```

#### `MATCH (n:Movie {title: "Speed Racer"}) RETURN n`

`{title: "Speed Racer"}`는 속성 조건이다. 아래 `WHERE` 문과 결과가 같다.

```cypher
MATCH (n:Movie)
WHERE n.title = "Speed Racer"
RETURN n
```

| 구분 | `{ }` 조건 | `WHERE` 조건 |
|---|---|---|
| 비교 방식 | 같음(=)만 가능 | `>`, `<`, `<>`, `CONTAINS`, `STARTS WITH`, `AND`, `OR` 등 |
| 쓰임 | 값이 정확히 같은지만 볼 때 | 범위, 부분 일치, 복합 조건 |

```cypher
MATCH (m:Movie) WHERE m.released >= 2000 RETURN m.title, m.released
```

```cypher
MATCH (m:Movie) WHERE m.title CONTAINS "Matrix" RETURN m.title
```

> [!warning] 대소문자를 구분한다
> 문자열 값과 속성 이름은 대소문자를 구분한다. `"speed racer"`나 `Title`로는 찾지 못한다. 문자열은 `"..."`와 `'...'` 모두 쓸 수 있다.

#### `MATCH (n1)-[r]->(n2) RETURN n1, r, n2 LIMIT 50`

| 부분 | 의미 |
|---|---|
| `(n1)` | 레이블이 없으므로 모든 노드가 대상이다 |
| `-[r]->` | 관계 유형이 없으므로 모든 관계가 대상이다. n1에서 n2로 가는 방향 |
| `(n2)` | 관계의 도착 노드 |
| `RETURN n1, r, n2` | 시작 노드, 관계, 도착 노드를 모두 돌려주므로 Browser가 선으로 이어진 그림을 그린다 |

화살표 없이 `-[r]-`로 쓰면 방향을 따지지 않으므로 같은 관계가 두 번씩 나온다.

같은 `( )-[ ]->( )` 모양에 레이블, 관계 유형, 속성을 하나씩 채우면 물음이 구체적으로 좁혀진다.

| 패턴 | 뜻 |
|---|---|
| `(n1)-[r]->(n2)` | 어떤 노드든 어떤 관계로든 이어진 것 |
| `(p:Person)-[r]->(m:Movie)` | 사람과 영화 사이의 모든 관계 |
| `(p:Person)-[:ACTED_IN]->(m:Movie)` | 사람이 영화에 출연한 관계만 |
| `(p:Person {name: "Tom Hanks"})-[:ACTED_IN]->(m:Movie)` | Tom Hanks가 출연한 영화 |

```cypher
// Tom Hanks가 출연한 영화
MATCH (p:Person {name: "Tom Hanks"})-[:ACTED_IN]->(m:Movie)
RETURN p, m
```

```cypher
// 관계의 속성: 배역 이름(roles)
MATCH (p:Person {name: "Tom Hanks"})-[r:ACTED_IN]->(m:Movie)
RETURN m.title, r.roles
```

```cypher
// 한 영화의 감독과 배우. 화살표는 저장된 방향(사람 → 영화)을 따라 그린다
MATCH (d:Person)-[:DIRECTED]->(m:Movie {title: "The Matrix"})<-[:ACTED_IN]-(a:Person)
RETURN d.name, a.name
```

#### 절의 순서

```
MATCH     무엇을 찾을지 (패턴)
WHERE     조건
RETURN    무엇을 돌려줄지
ORDER BY  정렬
LIMIT     개수 제한
```

```cypher
MATCH (m:Movie)
WHERE m.released >= 2000
RETURN m.title, m.released
ORDER BY m.released DESC
LIMIT 10
```

#### 그 밖의 주요 명령

조회와 가공

| 명령 | 역할 | 예 |
|---|---|---|
| `OPTIONAL MATCH` | 패턴이 없어도 행을 남긴다. 없는 부분은 `null`. SQL의 `LEFT JOIN` | `MATCH (m:Movie) OPTIONAL MATCH (m)<-[:REVIEWED]-(r) RETURN m.title, count(r)` |
| `WITH` | 중간 결과를 다음 단계로 넘긴다. 집계 결과에 다시 조건을 걸 때 쓴다 | `MATCH (p:Person)-[:ACTED_IN]->(m) WITH p, count(m) AS n WHERE n >= 5 RETURN p.name, n` |
| `DISTINCT` | 중복 제거 | `RETURN DISTINCT co.name` |
| `UNWIND` | 리스트를 행으로 펼친다 | `UNWIND ['The Matrix', 'Top Gun'] AS t MATCH (m:Movie {title: t}) RETURN m` |
| `SKIP` | 앞의 N개를 건너뛴다 | `RETURN m.title ORDER BY m.title SKIP 5 LIMIT 3` |
| `EXISTS { }` | 패턴이 있는지 검사한다 | `MATCH (p:Person) WHERE NOT EXISTS { (p)-[:ACTED_IN]->() } RETURN p.name` |

쓰기 (데이터를 바꾼다)

| 명령 | 역할 |
|---|---|
| `CREATE` | 노드나 관계를 새로 만든다. 같은 것이 있어도 또 만든다 |
| `MERGE` | 있으면 찾고, 없으면 만든다. 중복 생성을 막는다 (7장 `add_graph_documents` 내부) |
| `SET`, `REMOVE` | 속성이나 레이블을 추가·변경하거나 지운다 |
| `DELETE` | 노드나 관계를 지운다. 관계가 남은 노드는 지울 수 없다 |
| `DETACH DELETE` | 노드와 연결된 관계를 함께 지운다 (7장 실습 전 초기화) |

> [!note] 샌드박스에서는 쓰기 명령을 실행하지 않는다
> 문법만 확인하려면 앞에 `EXPLAIN`을 붙인다. `EXPLAIN CREATE (p:Person {name: 'Test'})`는 실제로 노드를 만들지 않는다.

함수와 경로

| 종류 | 예 | 설명 |
|---|---|---|
| 집계 함수 | `count()`, `sum()`, `avg()`, `min()`, `max()`, `collect()` | `collect()`는 값을 리스트로 모은다 |
| 일반 함수 | `size()`, `coalesce()`, `toLower()`, `date()` | `coalesce(a, b)`는 a가 `null`이면 b를 쓴다 |
| 가변 길이 관계 | `-[:ACTED_IN*1..2]-` | 1~2 hop을 한 번에 탐색한다 |
| 최단 경로 | `shortestPath((a)-[*]-(b))` | 두 노드 사이의 가장 짧은 경로 |

### 3장 실습 과제

Browser에서 쿼리를 작성해 실행한다. 6장에서 같은 쿼리를 Python에서 다시 쓰므로 메모장에 저장해 둔다.

1. Tom Hanks가 출연한 영화 제목만 조회하라.
2. 2000년 이후 개봉한 영화를 개봉 연도순으로 10개 조회하라.
3. Keanu Reeves와 함께 출연한 배우 이름을 중복 없이 조회하라. (힌트: 같은 영화로 들어오는 `ACTED_IN` 두 개, `DISTINCT`)

---

## 4. Recommendations 그래프 데이터셋으로 Cypher 쿼리 실습

영화 평점 데이터로 Cypher를 연습하고, 파라미터 쿼리로 추천 쿼리를 실행한다.

| 항목 | 내용 |
|---|---|
| 연결할 DB | Recommendations (샌드박스는 2-1, Docker는 `bolt://localhost:7687`) |
| Browser | 샌드박스 Open, 또는 Docker http://localhost:7474 |
| 노트북 | `notebooks/ch04_cypher_recommendations.ipynb` (4-3, 실습 과제) |
| 연결 셀에서 보여야 하는 레이블 | Actor, Movie, Director, User, Genre |

Browser, 샌드박스에서 실습한다.  이후 5·6장(파이썬 환경 구성)을 마친 뒤 노트북 `ch04`에서 Python으로 다시 실행한다. 노트북을 열 때는 .env를 Recommendations 접속 정보로 바꾸고 커널을 재시작한다(5-5).

### 4-1. Recommendations 데이터셋

출처: https://github.com/neo4j-graph-examples/recommendations

| 노드 | 의미 |
|---|---|
| Movie | 영화(title, plot, year, imdbRating 등) |
| Actor, Director, Person | 배우, 감독, 인물 |
| Genre | 장르 |
| User | 평점을 남긴 사용자 |

| 관계 | 의미 |
|---|---|
| (Actor)-[:ACTED_IN]->(Movie) | 출연 |
| (Director)-[:DIRECTED]->(Movie) | 감독 |
| (Movie)-[:IN_GENRE]->(Genre) | 장르 분류 |
| (User)-[:RATED {rating}]->(Movie) | 별점 |

> [!note] Movies와 다른 점
> 3·6장의 Movies 데이터와 레이블, 속성이 다르다. 배우는 `Person`이 아니라 `Actor`이고, 개봉 연도는 `year`(숫자)다. `released`는 `'1995-11-22'` 같은 문자열이다. 처음 보는 DB에서는 먼저 `CALL db.schema.visualization`으로 구조를 확인한다.

### 4-2. 기본 조회 (Neo4j Browser)

Browser에서 한 쿼리씩 실행한다. Docker는 http://localhost:7474 에서 사용자 `neo4j`, 비밀번호 `graphrag-class`로 접속한다.

```cypher
// 특정 사용자가 평가한 영화 (조건 없이 실행하면 오래 걸린다)
MATCH (u:User {name: "Pamela Anthony"})-[r]->(m:Movie)
RETURN u, r, m
```

```cypher
// Batman 출연 배우
MATCH (a:Actor)-[:ACTED_IN]->(m:Movie {title: "Batman"})
RETURN a.name
```

```cypher
// 미국 출생, 1960년 이후 출생 인물, 출생일 순
MATCH (p:Person)
WHERE date(p.born) >= date('1960-01-01') AND p.bornIn CONTAINS "USA"
RETURN p
ORDER BY date(p.born) ASC
LIMIT 10
```

### 4-3. 파라미터 쿼리

값을 쿼리 문자열에 직접 붙이지 않고 `$파라미터`로 넘긴다.

- 같은 쿼리를 값만 바꿔 다시 쓸 수 있다.
- 따옴표 처리 실수와 Cypher 주입 공격을 막는다.

Browser에서는 `:param`으로 값을 먼저 정한 뒤 쿼리를 실행한다.

```cypher
:param movie => 'Crimson Tide'
```

```cypher
MATCH (m:Movie {title: $movie})<-[:RATED]-(u:User)-[:RATED]->(rec:Movie)
RETURN DISTINCT rec.title AS recommendation
LIMIT 20
```

Python(노트북 `ch04`)에서는 `graph.query()`의 `params`로 넘긴다. `graph`를 만드는 방법은 6-2에 있다.

```python
recommend_query = """
MATCH (m:Movie {title: $movie})<-[:RATED]-(u:User)-[:RATED]->(rec:Movie)
RETURN DISTINCT rec.title AS recommendation
LIMIT 20
"""
for row in graph.query(recommend_query, params={"movie": "Crimson Tide"}):
    print(row["recommendation"])
```

패턴 읽기: Crimson Tide를 평가한 사용자(u)가 평가한 다른 영화(rec). 영화 → 사용자 → 다른 영화로 이동하는 2-hop 추천이고, 가장 단순한 협업 필터링이다.

```
(Crimson Tide) <-[:RATED]- (u:User) -[:RATED]-> (rec:Movie)
     영화          1-hop      사용자      2-hop       추천 영화
```

### 4장 실습 과제

Browser에서 먼저 풀고, 노트북 `ch04`를 실행할 때 맨 아래 빈 셀에 Python으로 다시 작성한다. 모두 4-3의 추천 쿼리를 고쳐서 시작한다.

1. 추천 쿼리를 수정해 Crimson Tide에 별점 4.0 이상을 준 사용자만 대상으로 하라. (힌트: `-[r:RATED]-`, `WHERE r.rating >= 4.0`)
2. 추천 결과를 겹친 사용자 수가 많은 순서로 정렬하라. (힌트: `count(u)`, `ORDER BY`)
3. Drama 장르이고 imdbRating이 8.5 이상인 영화를 `graph.query()`로 조회하라. (힌트: 장르는 속성이 아니라 `Genre` 노드다)

---

## 5. 실습 환경 준비

노트북을 실행하기 위한 준비다. 미리 해 두면 6장 실습이 여유로워진다.

| 단계 | 할 일 | 확인 방법 |
|---|---|---|
| 5-1 | uv, VS Code 설치 | `uv --version` |
| 5-2 | 배포 폴더 받기, `uv sync` | `.venv` 폴더가 생김 |
| 5-3 | .env 작성 | 0_start.ipynb에서 `API Key configured: True` |
| 5-4 | VS Code 커널 연결 | `sys.executable`이 `.venv` 경로 |
| 5-5 | Neo4j 준비와 노트북별 .env | 노트북 연결 셀에 노드 수가 나옴 |

### 5-1. 도구 설치

uv는 Python 설치, 가상환경 생성, 패키지 관리를 한 도구로 처리한다. uv.lock 파일 덕분에 모든 교육생이 강사와 같은 버전을 쓴다.

1. PowerShell에서 uv를 설치한다.

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    # 또는
    winget install --id=astral-sh.uv -e
    ```

    설치 후 터미널을 새로 열고 `uv --version`으로 확인한다.

2. VS Code를 설치하고 확장 두 개를 설치한다.

    | 확장 | ID | 용도 |
    |---|---|---|
    | Python | ms-python.python | 인터프리터 선택, 실행, 디버깅 |
    | Jupyter | ms-toolsai.jupyter | VS Code 안에서 .ipynb 실행 |

### 5-2. 실습 폴더 구성

이 저장소의 `8_graph-rag/2026-graph-rag` 폴더를 `c:\study\2026-graph-rag`로 복사하고 아래를 실행한다.

```powershell
cd c:\study\2026-graph-rag
uv sync
copy .env.example .env
code .
```

`uv sync`는 uv.lock에 적힌 버전 그대로 `.venv`를 만든다. Python 3.12가 없으면 uv가 내려받는다.

완성된 폴더 구조

```
c:\study\2026-graph-rag\
├── .venv\                  # uv sync가 만든 가상환경
├── .env                    # 내 접속 정보 (공유하지 않는다)
├── .env.example            # 값을 비운 견본
├── .python-version         # 3.12
├── pyproject.toml          # 의존성 목록
├── uv.lock                 # 고정된 버전
├── .vscode\
│   └── settings.json       # 노트북 작업 위치를 프로젝트 루트로 고정
├── tools\
│   └── graphrag_tools.py   # .env 로드, 환경 확인, Neo4j 연결 도구 함수
├── docker\                 # Docker로 Neo4j를 띄울 때 사용
└── notebooks\
    ├── 0_start.ipynb       # 환경 확인
    └── ch04, ch06~ch09_*.ipynb  # 실습 노트북 (장 번호 = 가이드 장)
   ```

> [!warning] 노트북에서 `%pip install`을 쓰지 않는다
> 패키지는 `uv sync`로 이미 설치되어 있다. uv가 만든 .venv에는 pip이 없어 `%pip`은 실패하고, 성공하더라도 다른 교육생과 환경이 달라진다. 패키지가 더 필요하면 VS Code 터미널에서 `uv add 패키지명`을 실행한 뒤 커널을 재시작한다.

### 5-3. .env 파일 작성

`.env`는 노트북이 읽는 접속 정보 파일이다. OpenAI 키와 Neo4j 접속 정보 네 줄을 넣는다. `.env.example`에 노트북별 접속 정보가 주석으로 정리되어 있다.

```bash
OPENAI_API_KEY=발급받은_키
NEO4J_URI=bolt://xxx.xxx.xxx.xxx:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=발급받은_비밀번호
NEO4J_DATABASE=neo4j
```

- `=` 뒤에 값만 붙여 넣는다. 따옴표와 공백을 넣지 않는다.
- `OPENAI_API_KEY=OPENAI_API_KEY=sk-...`처럼 이름이 두 번 들어가면 401 인증 오류가 난다.
- 편집 후 반드시 저장(Ctrl+S)한다.
- NEO4J 네 줄은 노트북마다 바뀐다(5-5).

> [!danger] .env는 공유하지 않는다
> 공유 폴더, 화면 공유, 메신저, Notion, 깃 저장소에 올리지 않는다. 키가 노출되면 즉시 OpenAI 대시보드에서 폐기하고 새로 발급한다.

### 5-4. VS Code에서 노트북 커널 연결

1. `code .`로 **프로젝트 루트 폴더**를 연다. `notebooks` 폴더만 따로 열면 `.vscode\settings.json`이 적용되지 않는다.
2. `notebooks\0_start.ipynb`를 연다.
3. 오른쪽 위 `Select Kernel` → `Python Environments` → `.venv (Python 3.12.x)`를 고른다.
4. 셀을 실행해 `API Key configured: True`가 나오는지 확인한다.
5. 새 셀에서 커널과 작업 위치를 확인한다.

    ```python
    import os, sys
    print(sys.executable)   # c:\study\2026-graph-rag\.venv\Scripts\python.exe
    print(os.getcwd())      # c:\study\2026-graph-rag (notebooks가 아니어야 한다)
    ```

VS Code는 노트북마다 커널을 기억하므로 노트북을 처음 열 때 한 번만 고르면 된다.

### 5-5. Neo4j 준비와 노트북별 .env

 1. Neo4j를 어디에 띄우는가

| 방식            | 준비             | 접속 주소 형식                          | 주의                   |
| ------------- | -------------- | --------------------------------- | -------------------- |
| Neo4j Sandbox | 브라우저 로그인       | `bolt://IP:7687`                  | 생성 후 3일이면 사라진다       |
| AuraDB Free   | 브라우저 로그인       | `neo4j+s://ID.databases.neo4j.io` | DB 이름이 인스턴스 ID일 수 있다 |
| Docker (로컬)   | Docker Desktop | `bolt://localhost:7687`           | 처음 한 번 이미지 빌드        |

2. Sandbox: 만드는 방법과 credentials 파일을 .env에 옮기는 방법은 2-1에 있다.

3. AuraDB Free 만들기

	1. https://console.neo4j.io 에서 Create instance → AuraDB Free를 고른다.
	2. 생성 직후 credentials 파일(`Neo4j-<인스턴스ID>-Created-<날짜>.txt`)을 내려받는다. 비밀번호는 이때 한 번만 보여 준다.
	3. 파일의 `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` 네 줄을 그대로 .env에 옮긴다.
	4. 생성 후 약 60초가 지나야 접속된다. 오래 쓰지 않으면 일시 정지되므로 콘솔에서 Resume한다.

4. Docker로 띄우기

Docker Desktop이 실행 중인 상태에서 프로젝트 루트의 PowerShell에서 실행한다.

```powershell
docker compose -f docker/docker-compose.yml up -d --build --wait
```

처음에는 이미지를 빌드하고 예제 데이터(Recommendations, POLE)를 내려받아 적재하므로 몇 분 걸린다. `--wait`는 세 DB가 접속 가능해질 때까지 기다린다. 명령이 끝나기 전에 노트북을 연결하면 `ServiceUnavailable` 오류가 난다.

| 서비스           | 데이터             | NEO4J_URI               | Browser 주소            |
| ------------- | --------------- | ----------------------- | --------------------- |
| `neo4j-reco`  | Recommendations | `bolt://localhost:7687` | http://localhost:7474 |
| `neo4j-pole`  | POLE            | `bolt://localhost:7688` | http://localhost:7475 |
| `neo4j-empty` | 빈 DB            | `bolt://localhost:7689` | http://localhost:7476 |

세 DB 모두 사용자 이름은 `neo4j`, 비밀번호는 `graphrag-class`다.

```powershell
docker compose -f docker/docker-compose.yml up -d --wait   # PC를 다시 켠 뒤 시작
docker compose -f docker/docker-compose.yml stop           # 정지 (데이터는 남는다)
docker compose -f docker/docker-compose.yml ps             # 상태 확인 (healthy여야 한다)
```

노트북별 .env 바꾸기

| 노트북             | 데이터             | Sandbox / AuraDB             | Docker                          |
| --------------- | --------------- | ---------------------------- | ------------------------------- |
| ch04, ch06, ch09 | Recommendations | Recommendations 샌드박스         | `bolt://localhost:7687`         |
| ch07, 10장 종합 과제 | 빈 DB            | AuraDB Free 또는 Blank Sandbox | `bolt://localhost:7689`         |
| ch08            | POLE            | POLE 샌드박스                    | `bolt://localhost:7688`         |

Docker를 쓸 때 .env 예시 (Recommendations)

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphrag-class
NEO4J_DATABASE=neo4j
```

> [!important] .env를 바꾼 뒤에는 반드시 커널을 재시작한다
> 노트북의 `load_dotenv()`는 이미 읽은 값을 덮어쓰지 않는다. .env만 고치고 커널을 그대로 두면 이전 DB에 계속 연결된다. 노트북 상단의 `Restart`를 누르고 처음 셀부터 다시 실행한다.

여러 DB의 접속 정보를 .env에 주석(`#`)으로 보관해 두고, 쓸 네 줄만 주석을 푸는 방식이 편하다. 같은 이름의 줄이 주석 없이 두 번 나오지 않게 한다.

연결 확인 (터미널)

노트북을 열기 전에 VS Code 터미널(프로젝트 루트)에서 접속을 확인할 수 있다.

```powershell
uv run python -c "from dotenv import load_dotenv; import os; from neo4j import GraphDatabase; load_dotenv(); d=GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))); d.verify_connectivity(); print('Neo4j 연결 성공', d.execute_query('MATCH (n) RETURN count(n) AS c', database_=os.getenv('NEO4J_DATABASE')).records[0]['c'])"
```

### 5-6. 자주 나는 오류

| 증상 | 원인 | 조치 |
|---|---|---|
| 다른 DB의 데이터가 나온다, 노드가 없다는 오류 | .env를 고쳤지만 커널에 이전 값이 남아 있음 | 커널 재시작 후 처음부터 실행 |
| `ServiceUnavailable` (Docker) | 컨테이너가 꺼져 있거나 아직 시작 중 | `docker compose ... up -d --wait` 후 재시도 |
| `ServiceUnavailable: Unable to retrieve routing information` (AuraDB) | 대부분 TLS 인증서 검증 실패 | PowerShell에서 `Invoke-WebRequest https://<ID>.databases.neo4j.io -UseBasicParsing`를 한 번 실행 후 재시도. 그래도 안 되면 강사에게 알린다 |
| AuraDB 연결 실패 | 인스턴스 생성 직후, 또는 일시 정지 | 60초 기다리거나 콘솔에서 Resume |
| `AuthError: Unauthorized` | 비밀번호가 이 DB 것이 아님 | credentials 파일 값을 다시 옮긴다 |
| `Database does not exist` | `NEO4J_DATABASE` 값이 틀림 | credentials 파일의 값을 쓴다 |
| `Could not use APOC procedures` | DB에 APOC 플러그인이 없음 | 강사가 안내한 DB(Sandbox, AuraDB, 실습용 Docker)를 쓴다 |
| `ModuleNotFoundError` | 커널이 .venv가 아닌 다른 Python | `Select Kernel`에서 `.venv` 선택 |
| `No module named 'tools'` | 노트북이 notebooks 폴더에서 실행됨 | 프로젝트 루트 폴더를 `code .`로 다시 연다 |
| 커널 목록에 .venv가 없음 | `uv sync` 전이거나 VS Code가 폴더를 다시 읽지 않음 | `uv sync` 후 명령 팔레트에서 `Developer: Reload Window` |
| 401 인증 오류 (OpenAI) | 키를 잘못 붙여 넣음 | `.env`의 `OPENAI_API_KEY=` 줄 확인, 저장 후 커널 재시작 |

---

## 6. Python 연결

3장에서 Browser로 실행한 쿼리를 Python 코드에서 실행한다. Python 실습은 모두 Recommendations DB로 한다. 4장과 같은 DB에 연결하므로 3장 쿼리는 Recommendations에 맞게 조금 고쳐 쓴다(4-1 "Movies와 다른 점").

| 항목 | 내용 |
|---|---|
| 노트북 | `notebooks/ch06_python_connect.ipynb` |
| 연결할 DB | Recommendations (Docker `bolt://localhost:7687` 또는 Recommendations 샌드박스) |
| .env | Recommendations DB의 NEO4J 네 줄 (5-5) |
| 먼저 할 일 | 5-1 ~ 5-4 |

시작 전 .env 확인 (Docker의 경우)

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphrag-class
NEO4J_DATABASE=neo4j
```

Recommendations 샌드박스를 쓰면 credentials 파일의 `bolt://` 주소와 비밀번호를 옮긴다(2-1). .env를 고쳤으면 커널을 재시작한다.

### 6-1. 환경 확인

노트북 첫 코드 셀은 커널과 작업 위치, 패키지 버전을 출력한다.

| 출력 | 정상 값 | 다르면 |
|---|---|---|
| Python | `...\2026-graph-rag\.venv\Scripts\python.exe` | `Select Kernel`에서 `.venv` 선택 |
| 작업 위치 | `...\2026-graph-rag` (notebooks가 아님) | 프로젝트 루트 폴더를 `code .`로 다시 연다 |
| 패키지 버전 | 강사 화면과 같음 | 터미널에서 `uv sync` |

### 6-2. Python에서 연결 확인

`Neo4jGraph`는 LangChain에서 Neo4j를 다루는 기본 객체다. 쿼리 실행과 스키마 조회를 함께 제공한다.

```python
import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

# .env의 접속 정보를 한 묶음으로 둔다
NEO4J = dict(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE"),
)
graph = Neo4jGraph(**NEO4J)

print(graph.query("RETURN 'connected' AS status"))
print(graph.schema)   # 노드 속성, 관계 속성, 관계 패턴을 문자열로 반환
```

- `NEO4J`는 접속 정보 네 개를 묶은 딕셔너리다. 뒤의 장에서 `Neo4jVector` 같은 다른 LangChain 객체를 만들 때도 `**NEO4J`로 그대로 넘긴다.
- 실습 노트북(ch04, ch06~ch09)의 연결 셀은 위 코드를 `tools/graphrag_tools.py`의 `connect_graph()` 한 줄로 실행한다. 함수 안에서 위와 같이 `NEO4J`를 만들고 `Neo4jGraph(**NEO4J)`로 연결한다. `expect`에 준 레이블이 DB에 없으면 다른 DB에 연결됐다고 알려 준다.

    ```python
    from tools.graphrag_tools import connect_graph
    graph, NEO4J = connect_graph(expect=["Movie", "User", "Genre"])
    ```

- 연결 셀은 레이블별 노드 수를 출력한다. Recommendations라면 Actor, Movie, Director, User, Genre가 보여야 한다.
- `graph.schema`는 8장 Text2Cypher에서 LLM에 넘길 스키마다. 3장의 `CALL db.schema.visualization`이 그림으로 보여 준 구조를 텍스트로 정리한 것이다. 구조가 바뀌면 `graph.refresh_schema()`로 다시 읽는다.

Recommendations 데이터베이스의 `graph.schema` (속성 순서는 실행마다 다를 수 있다)

```
Node properties:
Movie {url: STRING, runtime: INTEGER, revenue: INTEGER, imdbRating: FLOAT, released: STRING, countries: LIST, languages: LIST, plot: STRING, imdbVotes: INTEGER, imdbId: STRING, year: INTEGER, poster: STRING, movieId: STRING, tmdbId: STRING, title: STRING, budget: INTEGER}
Genre {name: STRING}
User {userId: STRING, name: STRING}
Actor {url: STRING, bornIn: STRING, bio: STRING, died: DATE, born: DATE, imdbId: STRING, name: STRING, poster: STRING, tmdbId: STRING}
Director {url: STRING, bornIn: STRING, born: DATE, died: DATE, tmdbId: STRING, imdbId: STRING, name: STRING, poster: STRING, bio: STRING}
Person {url: STRING, bornIn: STRING, bio: STRING, died: DATE, born: DATE, imdbId: STRING, name: STRING, poster: STRING, tmdbId: STRING}
Relationship properties:
RATED {rating: FLOAT, timestamp: INTEGER}
ACTED_IN {role: STRING}
DIRECTED {role: STRING}
The relationships:
(:Movie)-[:IN_GENRE]->(:Genre)
(:User)-[:RATED]->(:Movie)
(:Actor)-[:ACTED_IN]->(:Movie)
(:Actor)-[:DIRECTED]->(:Movie)
(:Director)-[:DIRECTED]->(:Movie)
(:Director)-[:ACTED_IN]->(:Movie)
(:Person)-[:ACTED_IN]->(:Movie)
(:Person)-[:DIRECTED]->(:Movie)
```

- 9장에서 줄거리 임베딩을 만든 DB에서는 Movie에 `embedding: LIST`가 더 보인다.
- 배우는 `Actor`와 `Person` 레이블을 함께 가진다. 그래서 3장의 `(p:Person)-[:ACTED_IN]->(m:Movie)` 패턴이 그대로 동작한다.

### 6-3. Browser 쿼리를 Python에서 실행

Browser에 입력한 쿼리는 `graph.query()`에 문자열로 넣으면 그대로 실행된다. 결과는 딕셔너리의 리스트로 돌아온다.

```python
rows = graph.query("""
MATCH (m:Movie)
WHERE m.year >= 2000
RETURN m.title AS title, m.year AS year
ORDER BY m.year DESC
LIMIT 5
""")
for row in rows:
    print(row["title"], row["year"])
```

`RETURN`에서 `AS`로 붙인 이름이 딕셔너리의 키가 된다. `AS`를 빼면 키가 `m.title`처럼 표현식 그대로 붙는다.

> [!warning] 3장 쿼리를 그대로 쓰면 결과가 비어 있다
> 3장 Movies의 `released`는 숫자(`2003`)지만 Recommendations의 `released`는 문자열(`'1995-11-22'`)이다. `WHERE m.released >= 2000`은 오류 없이 0행을 돌려준다. 개봉 연도는 `year`(숫자)를 쓴다.

### 6장 실습 과제

노트북 맨 아래 빈 셀에 작성한다.

1. 3장 실습 과제의 쿼리 세 개(Tom Hanks 출연작, 2000년 이후 개봉작 10편, Keanu Reeves 공동 출연자)를 Recommendations에 맞게 고쳐 `graph.query()`로 실행하고, 결과를 한 줄에 한 건씩 출력하라. 결과 수가 3장(Movies)과 어떻게 다른지도 확인한다.
2. `graph.schema` 출력에서 Movie 노드의 속성 목록을 찾아라. 문자열에서 찾는 방법 외에 `graph.structured_schema`에서 꺼내는 방법도 시도해 본다.

---

## 7. 텍스트로 지식 그래프 구축과 벡터 RAG

짧은 영어 텍스트에서 LLM으로 엔티티와 관계를 뽑아 Neo4j에 지식 그래프를 만들고, 원문 청크를 임베딩해 벡터 RAG 체인을 만든다.

| 항목 | 내용 |
|---|---|
| 노트북 | `notebooks/ch07_kg_vector_rag.ipynb` |
| 연결할 DB | **빈 DB** (AuraDB Free, Blank Sandbox, 또는 Docker `bolt://localhost:7689`) |
| 연결 셀에서 보여야 하는 것 | 노드 0개 |

> [!danger] 다른 데이터가 있는 DB에 연결하지 않는다
> 이 노트북은 DB에 데이터를 쓰고, 다시 실행할 때 `RESET_DB = True`로 DB 전체를 지운다. Recommendations나 POLE DB에 연결한 채로 실행하면 4·8·9장에서 쓸 데이터가 사라진다. 연결 셀 출력에서 `bolt://localhost:7689`(Docker) 또는 내 AuraDB 주소인지 먼저 확인한다.

> [!info] 이 장에서 새로 배우는 것
> 임베딩(7-3), 청크 분할(7-4), retriever(7-6의 `as_retriever`), LCEL RAG 체인(7-7)은 RAG 기초 과정에서 배운 내용을 Neo4j에 그대로 적용한 것이다. 이 부분은 복습으로 빠르게 실행하고, 새로 배우는 **7-5 지식 그래프 추출·적재**와 **7-6 Neo4j 벡터 인덱스**에 시간을 쓴다.

### 7-1. 빈 DB 준비

AuraDB Free를 쓰는 경우

1. https://console.neo4j.io 에서 Create instance → AuraDB Free로 인스턴스를 만들고 credentials 파일을 내려받는다. 비밀번호는 이때 한 번만 보여 준다.
2. credentials 파일의 `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` 네 줄을 .env에 옮기고 커널을 재시작한다.

Docker를 쓰는 경우

```bash
NEO4J_URI=bolt://localhost:7689
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=graphrag-class
NEO4J_DATABASE=neo4j
```

노트북을 다시 처음부터 실행할 때는 노트북의 "DB 비우기" 셀에서 `RESET_DB = True`로 바꿔 실행한다. 실행되는 쿼리는 다음과 같다.

```cypher
MATCH (n) DETACH DELETE n
```

### 7-2. 파이프라인 흐름

```
샘플 텍스트 → 청크 분할 → 엔티티·관계 추출(LLMGraphTransformer) → Neo4j 적재
            → 청크 임베딩과 벡터 인덱스(Neo4jVector) → retriever → LCEL RAG 체인
```

### 7-3. 임베딩 원리: OpenAI API 직접 호출

> [!note] 복습
> 임베딩, 코사인 유사도, `OpenAIEmbeddings`(`embed_query`, `embed_documents`)는 [임베딩](<../6_llm-app-dev/05_RAG_기초/05_임베딩.md>), [RAG 4장 유사도](<../6_llm-app-dev/05_RAG_기초/01_RAG.md>)에서 다뤘다. 여기서는 코드를 실행하고 아래 "관찰할 것"만 새로 확인한다.

```python
from openai import OpenAI
import numpy as np

client = OpenAI()
resp = client.embeddings.create(
    model="text-embedding-3-small",
    input=["마리 퀴리는 노벨상을 두 번 받았다.", "Marie Curie won two Nobel Prizes."],
)
v1, v2 = resp.data[0].embedding, resp.data[1].embedding
print(len(v1))   # 1536

cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
print(round(cos, 3))
```

> [!tip] 관찰할 것
> 뜻이 같은 한국어 문장과 영어 문장의 유사도가 생각보다 높은가, 낮은가? 영어 문서를 한국어 질문으로 검색하면 어떤 일이 생길지 생각해 본다. 문서와 질문의 언어를 맞추거나 질문을 문서 언어로 번역해 검색하는 이유다.

### 7-4. 청크 분할

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

sample_text = """
Marie Curie, 7 November 1867 - 4 July 1934, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
She was, in 1906, the first woman to become a professor at the University of Paris.
"""

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
documents = splitter.create_documents([sample_text])
print(len(documents))
```

> [!note] 복습
> `chunk_size`, `chunk_overlap`, `create_documents`는 [Splitter의 모든 것](<../6_llm-app-dev/05_RAG_기초/04_Splitter의_모든것.md>)에서 다뤘다. 샘플이 짧아서 300자로 잘라 청크가 여러 개 나오게 했다.

### 7-5. 엔티티·관계 추출과 적재

`LLMGraphTransformer`는 LLM에 청크를 주고 노드와 관계를 구조화된 형태로 받는다. 허용할 노드·관계 유형을 지정하면 결과가 일정해진다.

```python
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

llm = ChatOpenAI(model="gpt-4o", temperature=0)

transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Organization", "Award", "Country", "Field"],
    allowed_relationships=["MARRIED_TO", "WON", "WORKED_AT", "CITIZEN_OF", "RESEARCHED"],
)
graph_documents = transformer.convert_to_graph_documents(documents)

for gd in graph_documents:
    print(gd.nodes)
    print(gd.relationships)

graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)
```

| 옵션 | 의미 |
|---|---|
| `include_source=True` | 원문 청크를 `Document` 노드로 저장하고, 청크에서 엔티티로 `MENTIONS` 관계를 만든다. 답변 근거를 원문까지 추적할 수 있고, 7-6의 벡터 검색이 이 `Document`를 쓴다 |
| `baseEntityLabel=True` | 모든 엔티티에 `__Entity__` 레이블을 추가한다. 레이블과 상관없이 엔티티 전체를 찾을 때 쓴다 |

- 노드는 `MERGE`로 쓰므로 id가 같은 엔티티는 하나로 합쳐진다.
- 추출 품질은 모델에 크게 좌우된다. 같은 코드여도 옆 사람과 노드 수와 관계가 다를 수 있다.

Neo4j Browser에서 확인한다(Docker 빈 DB는 http://localhost:7476).

```cypher
MATCH (d:Document)-[:MENTIONS]->(e)-[r]->(e2)
RETURN d, e, r, e2 LIMIT 50
```

### 7-6. 벡터 인덱스와 retriever

`Neo4jVector.from_existing_graph`는 지정한 레이블의 노드 중 임베딩이 없는 노드를 찾아 임베딩하고, 벡터 인덱스까지 만든다.

```python
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jVector

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    **NEO4J,
    index_name="document_index",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
for doc in retriever.invoke("마리 퀴리가 노벨상을 받은 이유는?"):
    print(doc.page_content)
```

새로 볼 점은 벡터 저장소가 Chroma 같은 별도 DB가 아니라 **그래프와 같은 Neo4j**라는 것이다. 임베딩은 `Document` 노드의 `embedding` 속성에 저장되고, 같은 노드가 7-5의 `MENTIONS` 관계로 엔티티와 이어져 있다. 9장 하이브리드 검색이 이 연결을 쓴다.

> [!note] 복습
> `as_retriever(search_kwargs={"k": 3})`는 [리트리버](<../6_llm-app-dev/05_RAG_기초/08_리트리버.md>)와 같다. 문서와 질문은 같은 임베딩 모델로 임베딩해야 비교할 수 있다.

### 7-7. LCEL RAG 체인

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_messages([
    ("system", "주어진 문서만 근거로 한국어로 간결하게 답한다. 문서에 없으면 '정보가 부족합니다'라고 답한다."),
    ("human", "문서:\n{context}\n\n질문: {question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print(rag_chain.invoke("마리 퀴리가 노벨상을 받은 이유는 무엇인가요?"))
```

> [!note] 복습
> `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()`는 [ChatPromptTemplate·LCEL 체인과 프롬프트 설계](<../6_llm-app-dev/[배포용] 1_ChatPromptTemplate·LCEL 체인과 프롬프트 설계.md>)의 RAG 예시와 같은 패턴이다. 바뀐 것은 retriever가 Neo4j를 검색한다는 점뿐이다.

> [!tip] 관찰할 것
> 답변이 "정보가 부족합니다"로 나왔다면 왜 그런지 검색된 청크를 다시 읽어 본다. 문서에 노벨상을 받았다는 사실은 있지만, 받은 **이유**도 있는가? 시스템 프롬프트의 "주어진 문서만 근거로" 지시가 어떤 역할을 했는지 생각해 본다.

이 단계의 검색은 순수 벡터 검색이다. 추출한 엔티티와 관계는 그래프에 들어 있지만 답변에는 쓰이지 않는다. 그래프 관계를 검색에 쓰는 방법은 8장과 9장에서 다룬다.

### 7장 실습 과제

노트북 맨 아래 빈 셀에 작성한다.

1. `allowed_nodes`, `allowed_relationships`를 지우고 다시 추출해 결과를 비교하라. 노드 수, 레이블 종류, 관계 종류를 비교한다.
2. Pierre Curie의 경력 문장 3~4개를 추가해 적재하고, 새 노드가 기존 그래프와 어떻게 연결되는지 확인하라. 새 `Document`에도 임베딩이 필요하다는 점에 주의한다.
3. `k`를 1과 3으로 바꿔 답변 차이를 비교하라. 무엇이 검색됐는지도 함께 출력한다.

### 7장 자주 나는 오류

| 증상 | 원인 | 조치 |
|---|---|---|
| 연결 셀에서 `['Movie'] 레이블이 있는 DB에 연결됐습니다` 오류 | Recommendations나 POLE에 연결됨. 이 노트북이 그 DB를 지우지 않도록 멈춘 것 | .env를 빈 DB(Docker `bolt://localhost:7689`)로 바꾸고 커널 재시작 |
| 연결 셀에 노드가 이미 많다 | 빈 DB가 아닌 곳에 연결됨 | .env를 빈 DB로 바꾸고 커널 재시작 |
| `langchain_experimental` import 오류 | 패키지 버전 불일치 | 터미널에서 `uv sync` 후 커널 재시작 |
| 인덱스 차원 오류 | 같은 이름 인덱스가 다른 차원으로 이미 있음 | Browser에서 `DROP INDEX document_index` 후 재실행 |
| 실행할 때마다 노드가 늘어난다 | 이전 실행 결과가 남아 있음 | `RESET_DB = True`로 비운 뒤 처음부터 실행 |

---

## 8. Text2Cypher (POLE 데이터셋)

자연어 질문을 LLM으로 Cypher 쿼리로 바꿔 실행하고, 그 결과로 답변을 만든다. 먼저 OpenAI API로 직접 구현한 뒤 같은 기능을 `GraphCypherQAChain`으로 바꾼다.

| 항목 | 내용 |
|---|---|
| 노트북 | `notebooks/ch08_text2cypher.ipynb` |
| 연결할 DB | POLE (Sandbox 또는 Docker `bolt://localhost:7688`) |
| 연결 셀에서 보여야 하는 레이블 | Crime, Location, PostCode, Officer, Person 등 |

.env를 POLE 접속 정보로 바꾸고 커널을 재시작한 뒤 시작한다. Docker의 Browser 주소는 http://localhost:7475 다.

### 8-1. POLE 데이터셋

출처: https://github.com/neo4j-graph-examples/pole

POLE은 Person, Object, Location, Event의 약자로, 범죄 수사에서 인물·물건·장소·사건의 관계를 모델링한 데이터셋이다.

| 주요 노드 | 주요 관계 |
|---|---|
| Person, Officer, Crime, Location, PostCode, Area, Phone, PhoneCall, Vehicle, Object | (Crime)-[:OCCURRED_AT]->(Location), (Crime)-[:INVESTIGATED_BY]->(Officer), (Person)-[:PARTY_TO]->(Crime), (Person)-[:KNOWS]->(Person) |

```python
graph.refresh_schema()
print(graph.schema)
```

이 스키마 문자열이 LLM이 아는 DB 구조의 전부다. 여기 없는 레이블과 속성은 LLM이 알 수 없다.

### 8-2. Text2Cypher 동작 원리

```
질문 + 스키마 + few-shot 예시 → LLM → Cypher → Neo4j 실행 → 결과 → LLM → 자연어 답변
```

LLM이 쿼리를 정확히 만들려면 두 가지가 필요하다.

1. 스키마: 어떤 레이블, 속성, 관계가 있는지. `graph.schema`를 그대로 쓴다.
2. few-shot 예시: 질문과 정답 쿼리 쌍 2~3개.

LLM을 두 번 호출한다. 첫 번째는 쿼리를 만들고, 두 번째는 쿼리 결과를 문장으로 바꾼다. 두 프롬프트의 차이는 1-6에 있다.

### 8-3. OpenAI API로 직접 구현

체인 없이 직접 만들어 보면 Text2Cypher가 "프롬프트 + LLM 호출 + 쿼리 실행"의 조합이라는 점이 드러난다. few-shot 예시는 user와 assistant 메시지 쌍으로 넣는다.

```python
from openai import OpenAI

client = OpenAI()

SYSTEM = """너는 Neo4j Cypher 전문가다. 아래 스키마에 있는 레이블, 관계, 속성만 사용해
사용자 질문에 답하는 Cypher 쿼리 하나를 작성한다. 설명 없이 쿼리만 출력한다.

스키마:
{schema}"""

FEW_SHOTS = [
    ("Piccadilly에서 발생한 범죄 건수는?",
     "MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location {address: 'Piccadilly'})\nRETURN count(c) AS crime_count"),
    ("M22 8ER 우편번호 지역의 범죄 유형 분포는?",
     "MATCH (pc:PostCode {code: 'M22 8ER'})<-[:HAS_POSTCODE]-(l:Location)<-[:OCCURRED_AT]-(c:Crime)\nRETURN c.type, count(*) AS count ORDER BY count DESC"),
]

def text_to_cypher(question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM.format(schema=graph.schema)}]
    for q, cypher in FEW_SHOTS:
        messages += [{"role": "user", "content": q}, {"role": "assistant", "content": cypher}]
    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(model="gpt-4o", temperature=0, messages=messages)
    cypher = resp.choices[0].message.content.strip()
    return cypher.removeprefix("```cypher").removeprefix("```").removesuffix("```").strip()

def answer(question: str) -> str:
    cypher = text_to_cypher(question)
    rows = graph.query(cypher)
    print("생성된 Cypher:\n", cypher)
    resp = client.chat.completions.create(
        model="gpt-4o", temperature=0,
        messages=[
            {"role": "system", "content": "쿼리 결과만 근거로 한국어로 답한다."},
            {"role": "user", "content": f"질문: {question}\n쿼리 결과: {rows[:20]}"},
        ],
    )
    return resp.choices[0].message.content

print(answer("현재 수사 중인 범죄 사건의 개수는?"))
```

- `text_to_cypher`: 프롬프트 1. 쿼리만 출력하라고 해도 ```` ```cypher ```` 코드 블록으로 감싸 답할 때가 있어 벗겨 낸다.
- `answer`: 쿼리를 실행하고 결과로 프롬프트 2를 호출한다. 결과가 많으면 토큰이 커지므로 20행까지만 넘긴다.

### 8-4. GraphCypherQAChain으로 바꾸기

`GraphCypherQAChain`은 8-3의 두 단계를 하나의 체인으로 묶는다. few-shot 예시는 `cypher_prompt`에 넣는다.

```python
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain

CYPHER_TEMPLATE = """너는 Neo4j Cypher 전문가다. 스키마에 있는 레이블, 관계, 속성만 사용해 쿼리 하나를 작성한다.
설명 없이 쿼리만 출력한다.

스키마:
{schema}

예시:
질문: Piccadilly에서 발생한 범죄 건수는?
쿼리: MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location {{address: 'Piccadilly'}}) RETURN count(c) AS crime_count

질문: M22 8ER 우편번호 지역의 범죄 유형 분포는?
쿼리: MATCH (pc:PostCode {{code: 'M22 8ER'}})<-[:HAS_POSTCODE]-(l:Location)<-[:OCCURRED_AT]-(c:Crime) RETURN c.type, count(*) AS count ORDER BY count DESC

질문: {question}
쿼리:"""

cypher_prompt = PromptTemplate(input_variables=["schema", "question"], template=CYPHER_TEMPLATE)

cypher_chain = GraphCypherQAChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    graph=graph,
    cypher_prompt=cypher_prompt,
    validate_cypher=True,             # 관계 방향 오류를 스키마 기준으로 교정
    return_intermediate_steps=True,   # 생성된 쿼리와 조회 결과를 함께 반환
    allow_dangerous_requests=True,    # LLM이 만든 쿼리를 실행하므로 명시적 동의가 필요
    verbose=True,
)

result = cypher_chain.invoke({"query": "범죄자는 아니지만 범죄자를 가장 많이 알고 있는 사람은?"})
print(result["result"])
print(result["intermediate_steps"][0]["query"])
```

> [!warning] 템플릿 안의 Cypher 중괄호는 두 번 쓴다
> `{schema}`, `{question}`처럼 한 번 쓴 중괄호는 템플릿 변수로 해석된다. Cypher의 속성 중괄호는 `{{address: 'Piccadilly'}}`처럼 두 번 써야 한다. 한 번만 쓰면 변수가 없다는 오류가 난다.

| 반환값 | 내용 |
|---|---|
| `result["result"]` | 최종 답변 |
| `result["intermediate_steps"][0]["query"]` | LLM이 만든 Cypher |
| `result["intermediate_steps"][1]["context"]` | 쿼리 실행 결과 |

이 질문의 기준 쿼리는 다음과 같다. 사람에서 지인으로, 지인에서 범죄로 이어지는 2-hop 탐색, 부정 조건, 집계가 한 쿼리에 들어 있다. LLM이 만든 쿼리와 비교해 본다.

```cypher
MATCH (p:Person)-[:KNOWS]->(c:Person)-[:PARTY_TO]->(:Crime)
WITH p, count(DISTINCT c) AS known_criminals_count
WHERE NOT (p)-[:PARTY_TO]->(:Crime)
RETURN p.name, p.surname, known_criminals_count
ORDER BY known_criminals_count DESC
```

### 8-5. Text2Cypher의 정확성은 조건부다

- 벡터 검색으로는 "개수", "가장 많은" 같은 집계 질문에 답할 수 없다. Text2Cypher는 DB가 직접 계산하므로 이런 질문에 강하다.
- 하지만 그 계산을 지시하는 쿼리를 LLM이 만든다. 쿼리가 질문을 잘못 해석하면 **오류 없이 틀린 답**을 낸다.
- 그래서 생성된 쿼리를 항상 출력하고 Browser에서 검증한다.
- `allow_dangerous_requests=True`는 LLM이 `DELETE` 같은 쓰기 쿼리를 만들어도 실행된다는 뜻이다. 실제 서비스에서는 읽기 전용 계정으로 연결한다.

자주 생기는 쿼리 오류

- 관계 방향을 반대로 쓴다.
- 스키마에 없는 레이블이나 속성 이름을 지어낸다.
- 값의 표기가 데이터와 다르다(대소문자, 약어, 날짜 형식).
- 중복을 세거나 `DISTINCT`를 빠뜨린다.
- 동률이 있는데 `LIMIT 1`로 하나만 남긴다.

> [!tip] 생각해 볼 것: 사람을 세는가, 경로를 세는가
> 패턴 `(p)-[:KNOWS]->(c)-[:PARTY_TO]->(:Crime)`은 "지인–범죄" 경로마다 행을 하나씩 만든다. 범죄 2건에 연루된 지인은 두 번 세어진다. `count(c)`와 `count(DISTINCT c)`로 각각 실행해 상위 결과가 어떻게 달라지는지, 그리고 LLM이 만든 쿼리는 어느 쪽인지 확인해 본다.

### 8장 실습 과제

노트북 맨 아래 빈 셀에 작성한다.

1. "M22 8ER 지역에서 가장 많이 발생한 범죄 유형은?"을 직접 구현(8-3)과 체인(8-4)에 각각 질문하고, 생성된 쿼리를 Browser에서 검증하라.
2. few-shot 예시를 모두 뺀 프롬프트로 같은 질문을 실행해 생성 쿼리와 결과를 비교하라. 다른 설정은 그대로 둔다.
3. 8-3의 직접 구현과 8-4의 체인에 같은 질문 3개를 넣어 생성 쿼리를 비교하라.

---

## 9. Vector + Graph 하이브리드 RAG

벡터 검색으로 질문과 줄거리가 비슷한 영화를 찾고, 그 영화에서 출발하는 Cypher로 배우·장르 같은 관계 정보를 덧붙인다. 마지막에 Text2Cypher 결과까지 합쳐 하나의 답변을 만든다.

| 항목 | 내용 |
|---|---|
| 노트북 | `notebooks/ch09_hybrid_rag.ipynb` |
| 연결할 DB | Recommendations (Sandbox 또는 Docker `bolt://localhost:7687`) |
| 연결 셀에서 보여야 하는 레이블 | Actor, Movie, Director, User, Genre |

.env를 Recommendations 접속 정보로 바꾸고 커널을 재시작한 뒤 시작한다. 7·8장에서 다른 DB로 바꿔 두었다면 특히 주의한다.

### 9-1. 개념

하이브리드 검색은 두 단계로 진행된다.

1. 벡터 인덱스로 질문과 줄거리가 비슷한 Movie 노드를 찾는다.
2. 찾은 노드(`node`)에서 출발하는 Cypher(`retrieval_query`)로 배우, 장르 같은 관계 정보를 덧붙인다.

```
질문 → 임베딩 → 벡터 인덱스(moviePlotIndex) → 비슷한 Movie 5편 (node, score)
                                                 ↓ retrieval_query
                                    배우(ACTED_IN), 장르(IN_GENRE) 확장
                                                 ↓
                                    text + score + metadata
```

벡터 검색은 "마법 보드게임 영화"처럼 제목을 모르는 질문에 강하고, 그래프 탐색은 출연진 같은 구조화된 정보를 정확히 가져온다.

### 9-2. 줄거리 임베딩 확인

벡터 검색에는 영화 줄거리를 벡터로 바꿔 둔 `Movie.embedding` 속성과 벡터 인덱스 `moviePlotIndex`가 있어야 한다. 노트북의 "1. 줄거리 임베딩" 셀이 이것을 확인한다.

| 출력 | 뜻 | 할 일 |
|---|---|---|
| `RuntimeError: Movie 노드가 없습니다` | Recommendations가 아닌 DB에 연결됨 | .env를 Recommendations로 바꾸고 커널 재시작 |
| `임베딩된 영화 9083편` | 준비 완료 | 다음 셀로 진행 |
| `임베딩이 없습니다` | 아직 임베딩하지 않은 DB | 강사 안내에 따라 `RUN_EMBEDDING = True`로 바꿔 한 번 실행 |

`RUN_EMBEDDING = True`로 실행하면 7-6과 같은 함수가 대상만 바꿔 동작한다.

```python
Neo4jVector.from_existing_graph(
    embedding=embeddings,
    **NEO4J,
    index_name="moviePlotIndex",
    node_label="Movie",
    text_node_properties=["plot"],
    embedding_node_property="embedding",
)
```

- plot이 있는 영화 9,083편을 1,000편씩 나눠 임베딩한다. 1~2분 걸리고 비용은 약 $0.006이다.
- 이미 임베딩된 영화는 건너뛰므로, 다시 실행해도 비용이 다시 들지 않고 중간에 끊겨도 이어서 할 수 있다.
- 실행이 끝나면 `RUN_EMBEDDING = False`로 되돌려 둔다.

### 9-3. retrieval_query로 관계 정보 확장

`retrieval_query`는 벡터 검색 결과인 `node`와 `score`를 받아 이어서 실행되는 Cypher다. 반드시 `text`, `score`, `metadata` 세 항목을 반환해야 한다.

```python
retrieval_query = """
WITH node, score
OPTIONAL MATCH (node)<-[:ACTED_IN]-(actor:Actor)
OPTIONAL MATCH (node)-[:IN_GENRE]->(genre:Genre)
WITH node, score, collect(DISTINCT actor.name) AS actors, collect(DISTINCT genre.name) AS genres
RETURN node.plot AS text,
       score,
       {title: node.title, actors: actors, genres: genres} AS metadata
"""

hybrid_store = Neo4jVector.from_existing_index(
    embedding=embeddings,
    index_name="moviePlotIndex",
    **NEO4J,
    retrieval_query=retrieval_query,
)
hybrid_retriever = hybrid_store.as_retriever(search_kwargs={"k": 5})

for d in hybrid_retriever.invoke("What is the movie about the magic jungle board game?"):
    print(d.metadata["title"], d.metadata["genres"], d.metadata["actors"][:3])
```

| 반환 항목 | LangChain에서 |
|---|---|
| `text` | `Document.page_content` |
| `score` | 유사도 점수 |
| `metadata` | `Document.metadata` (딕셔너리) |

- `OPTIONAL MATCH`를 쓰는 이유: 배우나 장르가 없는 영화도 검색 결과에서 빠지지 않게 하려고.
- 중간 `WITH`에서 `score`를 넘기지 않으면 오류가 난다.
- `from_existing_index`는 이미 있는 인덱스에 연결만 한다. `from_existing_graph`와 달리 임베딩하지 않는다.

> [!tip] 해 볼 것
> `retrieval_query`에서 장르 줄을 지우고 같은 질문을 실행해 본다. 질문이 같아도 `retrieval_query`가 무엇을 반환하느냐에 따라 LLM에 들어갈 정보가 달라진다.

### 9-4. 벡터 문맥과 그래프 문맥을 합치는 LCEL 체인

벡터 검색 결과와 8장 방식의 Text2Cypher 결과를 하나의 프롬프트에 넣는다. `RunnableParallel`은 두 검색을 동시에 실행한다.

```python
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

movie_cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    validate_cypher=True,
    allow_dangerous_requests=True,
)

def format_movies(docs):
    return "\n\n".join(
        f"제목: {d.metadata['title']}\n장르: {', '.join(d.metadata['genres'])}\n"
        f"배우: {', '.join(d.metadata['actors'][:5])}\n줄거리: {d.page_content}"
        for d in docs
    )

def graph_context(question: str) -> str:
    try:
        return movie_cypher_chain.invoke({"query": question})["result"]
    except Exception as e:
        return f"그래프 조회 실패: {e}"

fusion_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "너는 영화 지식 도우미다. 벡터 검색 문맥과 그래프 조회 결과를 함께 고려해 사실에 근거한 한국어 답변을 작성한다. "
     "두 정보가 충돌하면 그래프 결과를 우선한다. 문맥에 없는 내용은 추측하지 않는다."),
    ("human",
     "질문: {question}\n\n[벡터 검색 문맥]\n{vector_context}\n\n[그래프 결과]\n{graph_context}\n\n"
     "요구사항: 가장 관련 있는 영화 1~3편의 제목, 장르, 주요 배우, 줄거리 요약을 제시하고 끝에 근거를 표기한다."),
])

hybrid_chain = (
    RunnableParallel(
        question=RunnablePassthrough(),
        vector_context=hybrid_retriever | format_movies,
        graph_context=RunnableLambda(graph_context),
    )
    | fusion_prompt
    | llm
    | StrOutputParser()
)

print(hybrid_chain.invoke("A cowboy doll and new spaceman figure in a boy's room?"))
print(hybrid_chain.invoke("What is the movie about the board game?"))
```

```
            ┌─ question:       질문 그대로 ───────────────────┐
질문 ───────┼─ vector_context: hybrid_retriever → format_movies ┼→ fusion_prompt → llm → 답변
            └─ graph_context:  Text2Cypher 결과 ──────────────┘
```

- `graph_context`에 예외 처리를 둔 이유: Text2Cypher가 실패해도 체인 전체가 멈추지 않고 벡터 문맥만으로 답하게 하려고.
- 충돌하면 그래프 결과를 우선하는 이유: 그래프 결과는 DB에 실제로 있는 사실이기 때문이다.

> [!tip] 관찰할 것: 답변의 내용이 문맥에 정말 있는가
> 두 번째 질문 "What is the movie about the board game?"의 답변에 나온 영화의 장르와 배우를 `vector_context`와 `graph_context`에 실제로 들어 있던 내용과 하나씩 대조해 본다. 각 문맥을 따로 출력하려면 `hybrid_retriever.invoke(질문)`과 `graph_context(질문)`을 실행한다. 문맥에 없는 정보가 답변에 들어 있다면 어디서 온 것일까? 실습 과제 3과 이어진다.

### 9장 실습 과제

노트북 맨 아래 빈 셀에 작성한다.

1. `retrieval_query`에 감독(`(d:Director)-[:DIRECTED]->(node)`)을 추가해 metadata로 반환하라.
2. 4장의 협업 필터링 쿼리를 `retrieval_query`에 넣어, 검색된 영화를 높게 평가한 사용자가 좋아한 다른 영화까지 metadata로 반환하라.
3. 데이터에 없는 영화를 질문해 fusion_prompt의 "추측하지 않는다" 규칙이 지켜지는지 확인하라. 지켜지지 않으면 프롬프트를 고쳐 다시 실험한다.

---

## 10. 세 방식 비교와 종합 실습

7~9장에서 만든 세 가지 검색 방식을 비교하고, 각자 고른 텍스트로 GraphRAG를 처음부터 끝까지 만든다.

### 10-1. 세 방식 비교 토론

| 질문 | Vector | Text2Cypher | Vector + Graph |
|---|---|---|---|
| 마법 보드게임 영화의 출연진은? | 영화는 찾지만 출연진 정보 없음 | 제목을 모르면 쿼리 작성이 어려움 | 영화를 찾고 출연진까지 반환 |
| 수사 중인 사건은 몇 건인가? | 답할 수 없음 | 정확한 개수 | 부적합 |
| 마리 퀴리의 수상 이유는? | 원문 청크로 답변 | 관계만으로는 이유 설명 부족 | 청크와 관계를 함께 활용 |

토론 주제: 내가 만들 서비스의 질문 유형은 무엇이고, 세 방식 중 어떤 것을 기본으로 삼을지 정한다.

### 10-2. 종합 과제: 내 텍스트로 GraphRAG 만들기

7장에서 만든 지식 그래프와 섞이지 않도록 DB를 비우고 시작한다. Blank Sandbox를 새로 만들어 .env를 바꾸거나, 내 AuraDB 또는 Docker 빈 DB(`bolt://localhost:7689`)를 `MATCH (n) DETACH DELETE n`으로 비운다.

1. 3~5문단 분량의 텍스트를 고른다. 회사 소개, 위키 문서, 수업 자료 등 관계가 드러나는 글이 좋다.
2. 7장 코드로 지식 그래프를 만든다. `allowed_nodes`, `allowed_relationships`는 텍스트에 맞게 직접 정한다.
3. 같은 데이터에 세 방식으로 질문한다.
    - 벡터 RAG: 내용 요약형 질문 1개
    - Text2Cypher: 개수나 목록을 묻는 질문 1개
    - 하이브리드: 내용과 관계를 함께 묻는 질문 1개
4. 질문마다 생성된 Cypher(있는 경우), 답변, 정답 여부를 기록한다.

> [!tip] 막히는 지점
> - 하이브리드 검색의 `retrieval_query`는 7장 그래프 구조에 맞춰 써야 한다. 7장 그래프에서 원문은 `Document` 노드에 있고, 엔티티와는 `(Document)-[:MENTIONS]->(엔티티)`로 이어진다.
> - Text2Cypher 전에 `graph.refresh_schema()`로 새 그래프의 스키마를 다시 읽는다.
> - 정답 여부는 Browser에서 직접 쿼리를 실행해 확인한다.

제출물

| 방식 | 질문 | 생성된 Cypher | 답변 | 정답 여부 |
|---|---|---|---|---|
| 벡터 RAG | | (없음) | | |
| Text2Cypher | | | | |
| 하이브리드 | | | | |

그리고 "내 데이터에는 어떤 방식이 맞았는가"에 대한 한 문단.

### 10-3. 결과 공유

2~3명이 결과 표를 공유한다. 같은 질문 유형에서 방식별로 결과가 갈린 사례를 중심으로 이야기한다.

### 핵심 요약

1. 그래프 DB는 관계를 데이터로 저장해 멀티홉 탐색을 쿼리 한 줄로 표현한다.
2. Vector RAG는 의미 검색, Text2Cypher는 구조화된 질문과 집계, Vector + Graph는 의미 검색 결과를 관계로 확장할 때 쓴다.
3. Text2Cypher는 "스키마와 예시를 넣은 프롬프트 + LLM 호출 + 쿼리 실행"이다. `GraphCypherQAChain`은 이 과정을 묶은 것이다.
4. 하이브리드 RAG에서는 `retrieval_query` 설계가 답변에 들어갈 정보를 결정한다.

OpenAI API와 LangChain 대응표

| 기능 | OpenAI API 직접 | LangChain |
|---|---|---|
| 임베딩 | `client.embeddings.create` | `OpenAIEmbeddings` |
| LLM 호출 | `client.chat.completions.create` | `ChatOpenAI` |
| 프롬프트 | f-string, messages 리스트 | `ChatPromptTemplate`, `PromptTemplate` |
| Text2Cypher | 8-3 `text_to_cypher()` + `answer()` | `GraphCypherQAChain` |
| 벡터 저장·검색 | 직접 Cypher로 저장, `db.index.vector.queryNodes` 호출 | `Neo4jVector` |
| 파이프라인 연결 | 함수 호출 순서 | LCEL 파이프 연산자, `RunnableParallel` |

---

## 교육 종료 후 정리 (공용 PC인 경우)

1. 수업용 OpenAI 키를 폐기한다.
2. 필요 없는 AuraDB 인스턴스를 삭제한다.
3. 프로젝트 폴더를 삭제한다. .venv와 .env도 함께 지워진다.
4. uv 캐시를 지운다: `uv cache clean`, `uv python uninstall 3.12`
5. Docker를 썼다면 컨테이너와 데이터를 지운다: `docker compose -f docker/docker-compose.yml down -v`

## 참고 자료

- Neo4j Sandbox: https://sandbox.neo4j.com
- Neo4j AuraDB: https://console.neo4j.io
- Cypher 매뉴얼: https://neo4j.com/docs/cypher-manual/current/
- LangChain Neo4j 연동: https://python.langchain.com/docs/integrations/providers/neo4j/
- uv 문서: https://docs.astral.sh/uv/
