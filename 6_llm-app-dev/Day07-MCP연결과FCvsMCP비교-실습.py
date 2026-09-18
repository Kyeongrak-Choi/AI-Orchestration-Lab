# Day 7(M2 Day03) 실습 — MCP 연결과 FC vs MCP 비교
# 실행: uv run python notebook/M2-도구에이전트/Day07-MCP연결과FCvsMCP비교-실습.py
#
# 목표: MCP 서버(math_server.py)에 연결해 도구를 불러와 실행하고,
#       같은 기능(곱셈)을 Function Calling과 MCP 두 방식으로 만들어 비교한다.
#
# 참고: Windows·Jupyter에서는 MCP stdio 연결이 서브프로세스 제약으로 막힌다.
#       그래서 오늘 실습은 노트북이 아니라 .py 스크립트 + asyncio.run()으로 실행한다.

import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# math_server.py·review_server.py의 절대경로 (실행 위치가 어디든 안전)
MATH_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_server.py")
REVIEW_SERVER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "review_server.py"
)


# Part 2에서 쓸 Function Calling 버전 도구 (앱 코드 안에 직접 정의)


# Part 2-확장·Part 3에서 쓸 FC 버전 도구 (M2 Day02(Day06)와 동일한 mock)


# main() 함수를 정의한다.
async def main():
    # 클라이언트가 연결하려는 서버 정보를 포함해 클라이언트 객체를 생성한다.
    load_dotenv()
    llm = ChatOpenAI(model="gpt-4o-mini")

    client = MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,  # 현재 파이썬 (PATH의 "python"이 아님)
                "args": [MATH_SERVER],  # math_server.py만 실행
                "transport": "stdio",
            },
            "review": {
                "command": sys.executable,
                "args": [REVIEW_SERVER],  # review_server.py도 별도 MCP 서버로 실행
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()  # add, multiply, get_company_review
    print("=" * 100)
    print("서버로부터 받은 도구 목록 : ", [t.name for t in tools])

    # LLM에 툴 바인딩
    llm_with_tools = llm.bind_tools(tools)

    # 메시지로 생성
    question = "카카오의 리뷰 알려줘"
    messages = [HumanMessage(question)]

    # LLM에 툴 콜링
    ai_msg = await llm_with_tools.ainvoke(question)
    # print(ai_msg)

    # 툴콜링 결과를 메시지에 추가
    messages.append(ai_msg)

    # 툴 맵 생성
    tool_map = {t.name: t for t in tools}

    # 툴 실행
    for tc in ai_msg.tool_calls:
        result = await tool_map[tc["name"]].ainvoke(tc["args"])
        # print(result)
        messages.append(ToolMessage(str(result), tool_call_id=tc["id"]))

    # 최종응답 호출
    final = llm_with_tools.invoke(messages)
    print(final.content)
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())


# # ===== Part 1-5. 오류 다뤄보기 — 잘못된 서버 경로 =====
# print()
# print("===== Part 1-5. 오류 다뤄보기 — 잘못된 서버 경로 =====")

# # TODO: bad_server 경로로 MultiServerMCPClient를 하나 더 만드세요

# # ===== Part 1-6. command="python" vs sys.executable — 환경마다 다르다 =====
# print()
# print('===== Part 1-6. command="python" vs sys.executable =====')

# # TODO: command를 "python"으로 바꾼 naive_client를 만들어보세요 (환경에 따라 성공할 수도, 실패할 수도 있다)


# # ===== Part 2. Function Calling vs MCP 비교 =====
# print()
# print("===== Part 2. FC vs MCP 비교 (같은 기능: 곱셈) =====")

# # 2-1) FC 방식 — 앱 코드 안의 @tool
# # TODO: multiply를 bind_tools로 등록하세요


# 2-2) MCP 방식 — 별도 서버(math_server.py)의 multiply (Part1에서 이미 연결한 tools 재사용)
# TODO: tools(Part1에서 불러온 MCP 도구)를 bind_tools로 등록하세요

# # ===== Part 2-확장. 다른 도메인에 적용하기 — 회사 리뷰 도구도 FC vs MCP로 =====
# print()
# print("===== Part 2-확장. 회사 리뷰 도구 — FC vs MCP =====")


# # ===== Part 3. M2 통합 프로젝트 — 면접 코치의 도구를 혼합 소스로 구성 =====
# print()
# print("===== Part 3. M2 통합 — 면접 코치, FC+MCP 혼합 도구 =====")

# # TODO: ai_msg.tool_calls를 순회하며 coach_tool_map[name]을 ainvoke로 실행하고
# #       ToolMessage로 messages에 추가한 뒤, coach_llm을 다시 호출해 final을 만드세요
