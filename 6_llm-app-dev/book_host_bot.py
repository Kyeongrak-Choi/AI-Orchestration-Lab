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

BOOK_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),"book_server.py")


async def main():
    # 환경 로딩 & OpenAI API 연결
    load_dotenv()
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )

    # MCP 서버 연결
    client = MultiServerMCPClient(
        {
            "book": {
                "command": sys.executable,
                "args": [BOOK_SERVER],
                "transport": "stdio",
            }
        }
    )

    questions = ["베스트셀러 1위가 뭐야?", "헤세가 쓴 책 뭐 있어?"]

    # 도구 확인
    tools = await client.get_tools()
    print("사용 가능한 도구:", [tool.name for tool in tools])

    # llm에 도구 바인딩
    llm_with_tools = llm.bind_tools(tools)
    tool_map = {tool.name: tool for tool in tools}

    for question in questions:
        print(f"\n질문: {question}")

        # 툴콜즈: 모델이 도구를 호출할 때까지 질문을 보냅니다.
        messages = [HumanMessage(content=question)]
        ai_msg = await llm_with_tools.ainvoke(messages)
        messages.append(ai_msg)

        # 툴실행: 모델이 요청한 모든 MCP 도구를 실행하고 결과를 메시지로 돌려줍니다.
        # 한 번의 응답에서 여러 도구를 호출할 수 있으므로 반복 처리합니다.
        while ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool = tool_map.get(tool_name)

                if tool is None:
                    result = f"알 수 없는 도구입니다: {tool_name}"
                else:
                    try:
                        result = await tool.ainvoke(tool_call.get("args", {}))
                    except Exception as exc:
                        result = f"도구 실행 중 오류가 발생했습니다: {exc}"

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            # 도구 결과를 포함해 모델에 다시 요청합니다.
            ai_msg = await llm_with_tools.ainvoke(messages)
            messages.append(ai_msg)

        # 최종요청 결과를 출력합니다.
        print("답변:", ai_msg.content)


if __name__ == "__main__":
    asyncio.run(main())
