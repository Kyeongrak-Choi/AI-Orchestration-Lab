# Day 4 Part 3-미션 (실습) — MCP 자료실을 research_team 그래프의 첫 노드로 잇는다
#
# Day04-MCP자료실연결-정답.py는 자료를 받아 for 반복문으로 분석가 3명을 순서대로 불렀다 (그래프 없음, 통합자 없음).
# 이 파일은 같은 MCP 자료실을 노트북 Part 3의 fan-out + fan-in 그래프에 연결한다.
#
#   START → fetch(MCP get_source) → analyst × 3 (병렬) → aggregator → END
#
# 실행: 이 파일과 source_server.py가 있는 폴더에서  uv run python Day04-MCP자료실연결-그래프-실습.py
import asyncio
import operator
import os
import sys
import time
from pathlib import Path
from typing import Annotated

sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않게

# 추적 끄기: 2과목 Day17에서 .env의 LANGSMITH_TRACING을 켰다면 호출이 전부 전송된다
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

# 서버 경로는 이 파일 기준 절대경로로 — 어느 폴더에서 실행해도 찾을 수 있다 (2과목 Day 7 교훈)
SERVER = str(Path(__file__).parent / "source_server.py")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)  # 분석가: 관점마다 다양하게
llm_strict = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # 통합자: 흔들림 없이


# ── 노트북 Part 1~2에서 만든 부품 (그대로 옮겨 왔다) ──────────────────────────
class Analysis(BaseModel):
    points: list[str] = Field(description="이 관점에서 본 분석 포인트 3개. 각 포인트는 한 문장.")


class Report(BaseModel):
    title: str = Field(description="통합 보고서 제목")
    summary: str = Field(description="모든 관점을 종합한 요약 (3~4문장)")
    conflicts: list[str] = Field(description="관점이 서로 충돌하는 지점 (없으면 빈 리스트)")
    recommendation: str = Field(description="종합 판단 한 줄")


PERSPECTIVES = {
    "optimist": ("낙관 분석가", "이 서비스의 강점과 성장 기회를 찾는다"),
    "pessimist": ("비관 분석가", "이 서비스의 약점과 사업 위험을 찾는다"),
    "customer": ("고객 분석가", "이용자 입장에서 좋은 점과 불편한 점을 찾는다"),
    "finance": ("재무 분석가", "수익 구조와 비용 관점에서 지속 가능성을 분석한다."),
}


def analyze(key, source):
    """관점 key로 자료를 분석한다 (노트북 1-1과 같은 함수)."""
    name, mission = PERSPECTIVES[key]
    prompt = f"당신은 {name}입니다. 임무: {mission}.\n다음 자료를 분석해 포인트 3개를 내세요.\n\n[자료]\n{source}"
    result = llm.with_structured_output(Analysis).invoke(prompt)
    return {"perspective": name, "points": result.points}


def analyses_to_text(analyses):
    """분석 목록을 통합자에게 줄 글로 바꾼다."""
    lines = []
    for a in analyses:
        lines.append(f"[{a['perspective']}]")
        for p in a["points"]:
            lines.append(f"- {p}")
        lines.append("")
    return "\n".join(lines)


AGG_RULES = """- 각 관점을 공정하게 반영한다. 다수결로 뭉개지 않는다.
- 관점이 충돌하는 지점은 숨기지 말고 conflicts에 명시한다.
- 모든 내용은 한국어로 쓴다."""


def aggregate(analyses, rules=AGG_RULES):
    """통합자(Aggregator): 여러 분석을 하나의 보고서로 합친다."""
    prompt = f"당신은 통합자(Aggregator)입니다. 분석가들의 결과를 하나의 보고서로 합치세요.\n{rules}\n\n{analyses_to_text(analyses)}"
    return llm_strict.with_structured_output(Report).invoke(prompt)


def to_text(result):
    """MCP 도구 결과를 문자열로 바꾼다 (문자열 또는 [{"type": "text", "text": ...}] 목록)."""
    if isinstance(result, str):
        return result
    texts = []
    for block in result:
        texts.append(block["text"])
    return "\n".join(texts)


# ── 그래프 ─────────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    name: str  # 새 칸: 자료실에서 받을 자료 이름
    source: str
    analyses: Annotated[list[dict], operator.add]  # 병렬 기록을 리스트로 이어 붙인다
    report: dict


def build_team(get_source):
    """MCP 도구 get_source를 받아 자료 받기 → 병렬 분석 → 통합 그래프를 만든다."""

    async def fetch_node(state):
        # 자료실(MCP 서버)에서 원문을 받아 State의 source 칸에 담는다
        source = to_text(
            await get_source.ainvoke({"name": state["name"]})
        )
        return {"source": source}

    def dispatch(state):
        # fan-out: 관점마다 analyst 노드를 하나씩 보낸다
        return [Send("analyst", {"key": k, "source": state["source"]}) for k in PERSPECTIVES]

    def analyst_node(payload):
        return {"analyses": [analyze(payload["key"], payload["source"])]}

    def aggregator_node(state):
        r = aggregate(state["analyses"])
        return {"report": r.model_dump()}  # 계약 객체를 딕셔너리로 바꿔 State에 담는다

    g = StateGraph(ResearchState)
    g.add_node("fetch", fetch_node)
    g.add_node("analyst", analyst_node)
    g.add_node("aggregator", aggregator_node)
    
    g.add_edge(START, "fetch")
    g.add_conditional_edges("fetch", dispatch, ["analyst"])
    g.add_edge("analyst", "aggregator")
    g.add_edge("aggregator", END)
    return g.compile()


async def main():
    # 1) 자료실 서버에 연결하고 도구를 불러온다
    client = MultiServerMCPClient(
        {"library": {"command": sys.executable, "args": [SERVER], "transport": "stdio"}}
    )
    tools = await client.get_tools()
    tool_map = {}
    for t in tools:
        tool_map[t.name] = t
    print("[자료실 도구]", list(tool_map))

    # 2) MCP 도구를 넣어 그래프를 만든다
    research_team = build_team(tool_map["get_source"])

    # 3) 자료 이름만 넘긴다 — 원문은 그래프의 fetch 노드가 자료실에서 받아 온다
    start = time.time()
    result = await research_team.ainvoke(
        {"name": "새벽 수영 클럽", "analyses": []}
    )
    print("\n" + "=" * 60)
    print("MCP 자료실 기반 병렬 조사 결과")
    print("=" * 60)
    print(f"실행 시간: {time.time() - start:.1f}초")
    print(f"자료: {result['source'].splitlines()[0]}")
    print(f"분석가 수: {len(result['analyses'])}명")

    print("\n[관점별 분석]")
    for analysis in result["analyses"]:
        print(f"\n• {analysis['perspective']}")
        for index, point in enumerate(analysis["points"], start=1):
            print(f"  {index}. {point}")

    report = result["report"]
    print("\n[통합 보고서]")
    print(f"제목: {report['title']}")
    print(f"요약: {report['summary']}")
    print("충돌 지점:")
    if report["conflicts"]:
        for index, conflict in enumerate(report["conflicts"], start=1):
            print(f"  {index}. {conflict}")
    else:
        print("  없음")
    print(f"종합 판단: {report['recommendation']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
