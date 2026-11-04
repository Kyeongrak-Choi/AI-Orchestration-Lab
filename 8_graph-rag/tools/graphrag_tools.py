"""GraphRAG 실습 노트북에서 반복되는 설정 코드를 모은 도구 함수.

노트북은 프로젝트 루트에서 실행되므로(.vscode/settings.json) 아래처럼 불러온다.

    from tools.graphrag_tools import connect_graph
    graph, NEO4J = connect_graph()
"""
import os
import sys
from importlib.metadata import version

from dotenv import load_dotenv


def env_setting(override: bool = True) -> bool:
    """.env를 읽어 환경 변수로 등록하고 OpenAI 키가 있는지 출력한다.

    override=True이므로 .env를 고친 뒤 이 함수를 다시 실행하면 새 값이 반영된다.
    """
    load_dotenv(override=override)
    configured = bool(os.getenv("OPENAI_API_KEY"))
    print("API Key configured:", configured)
    return configured


def check_env(packages=("python-dotenv", "neo4j", "langchain-neo4j")) -> None:
    """커널 경로, 작업 위치, 패키지 버전을 출력한다."""
    print("Python :", sys.executable)   # ...\2026-graph-rag\.venv\Scripts\python.exe
    print("작업 위치:", os.getcwd())     # ...\2026-graph-rag (notebooks가 아니어야 한다)
    for pkg in packages:
        print(f"{pkg:26} {version(pkg)}")


def neo4j_config() -> dict:
    """.env의 Neo4j 접속 정보 네 개를 LangChain 객체에 넘길 수 있는 딕셔너리로 만든다.

    Neo4jGraph(**NEO4J), Neo4jVector.from_existing_graph(**NEO4J, ...)처럼 그대로 넘긴다.
    """
    load_dotenv(override=True)
    config = dict(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
    )
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise RuntimeError(f".env에 NEO4J 값이 비어 있습니다: {missing}. .env를 저장했는지 확인하세요.")
    return config


def connect_graph(expect=None, forbid=None, show_labels: bool = True):
    """Neo4jGraph로 연결하고 레이블별 노드 수를 출력한다. (graph, NEO4J)를 돌려준다.

    expect에 이 노트북에 있어야 하는 레이블을 주면, 없을 때 다른 DB에 연결됐다고 알려 준다.
    빈 DB가 맞는 노트북은 expect=[]로 둔다.
    forbid에 있으면 안 되는 레이블을 주면, 그 레이블이 있을 때 오류로 멈춘다.
    DB를 지우는 노트북이 예제 데이터가 든 DB에 연결되는 것을 막는다.
    """
    from langchain_neo4j import Neo4jGraph

    config = neo4j_config()
    graph = Neo4jGraph(**config)

    print("연결:", config["url"], "| DB:", config["database"])
    rows = graph.query("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC LIMIT 6")
    if show_labels:
        # 연결한 DB가 맞는지 레이블과 노드 수로 확인한다.
        for row in rows:
            print(row)

    if forbid:
        found = {row["label"] for row in graph.query("CALL db.labels() YIELD label RETURN label")}
        bad = [label for label in forbid if label in found]
        if bad:
            raise RuntimeError(
                f"{bad} 레이블이 있는 DB에 연결됐습니다. 이 노트북은 DB에 데이터를 쓰고 지우므로 빈 DB에서만 실행합니다. "
                ".env를 빈 DB(Docker bolt://localhost:7689 등)로 바꾸고 커널을 재시작하세요."
            )

    if expect is not None:
        if expect == [] and rows:
            print("주의: 빈 DB가 아닙니다. 다른 데이터가 있는 DB에 연결됐는지 .env를 확인하세요.")
        found = {row["label"] for row in graph.query("CALL db.labels() YIELD label RETURN label")}
        missing = [label for label in expect if label not in found]
        if missing:
            print(f"주의: {missing} 레이블이 없습니다. .env가 이 노트북의 DB를 가리키는지 확인하세요.")
    return graph, config
