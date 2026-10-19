# Day 4 Part 3-확장 (실습) — MCP 자료실에서 원문을 받아 분석 팀에 넘긴다
#
# 왜 .py인가: Windows·Jupyter에서는 MCP stdio 연결(서브프로세스)이 막힌다.
#            그래서 2과목 Day 7처럼 노트북이 아니라 .py + asyncio.run()으로 실행한다.
# 실행: 이 파일과 source_server.py가 있는 폴더에서  uv run python Day04-MCP자료실연결-실습.py
import asyncio
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔(cp949)에서 한글 출력이 깨지지 않게

# 추적 끄기: 2과목 Day17에서 .env의 LANGSMITH_TRACING을 켰다면 호출이 전부 전송된다
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# 서버 경로는 이 파일 기준 절대경로로 — 어느 폴더에서 실행해도 찾을 수 있다 (2과목 Day 7 교훈)
SERVER = str(Path(__file__).parent / "source_server.py")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


class Analysis(BaseModel):
    points: list[str] = Field(description="이 관점에서 본 분석 포인트 3개. 각 포인트는 한 문장.")


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


def to_text(result):
    """MCP 도구 결과를 문자열로 바꾼다.

    어댑터 버전에 따라 결과가 문자열이거나 [{"type": "text", "text": ...}] 목록으로 온다 → 둘 다 받는다.
    """
    if isinstance(result, str):
        return result
    texts = []
    for block in result:
        texts.append(block["text"])
    return "\n".join(texts)


async def main():
    # 1) 자료실 서버에 연결하고 도구를 불러온다
    client = MultiServerMCPClient(
        {
            "library": {
                "command": sys.executable,
                "args": [SERVER],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()
    tool_map = {}
    for t in tools:
        tool_map[t.name] = t
    print("[1.자료실 도구]", list(tool_map))

    # 2) 어떤 자료가 있는지 묻는다
    names = to_text(await tool_map["list_sources"].ainvoke({}))
    print("[2.자료 목록]", names)

    # 3) 없는 자료를 요청하면? — 서버가 안내 문구를 돌려준다
    missing = to_text(await tool_map["get_source"].ainvoke({"name": "한강 요가 모임"}))
    print("[3.없는 자료 요청]", missing)

    # 4) 자료를 받아 분석 팀에 넘긴다 — 분석가 코드는 자료가 어디서 왔는지 모른다
    source = to_text(
        await tool_map["get_source"].ainvoke({"name": "새벽 수영 클럽"})
    )
    print("\n[4.받은 자료 첫 줄]", source.splitlines()[0])

    for key in PERSPECTIVES:
        a = analyze(key, source)
        print(f"- [{a['perspective']}] {a['points'][0]}")


if __name__ == "__main__":
    asyncio.run(main())
