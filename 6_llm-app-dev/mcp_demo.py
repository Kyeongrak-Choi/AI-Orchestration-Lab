# mcp_demo.py
import asyncio, sys, os

sys.stdout.reconfigure(encoding="utf-8")

from langchain_mcp_adapters.client import MultiServerMCPClient

# math_server.py의 절대경로 (실행 위치가 어디든 안전)
SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_server.py")

async def main():
    client = MultiServerMCPClient({
        "math": {"command": sys.executable, "args": [SERVER], "transport": "stdio"}
    })
    tools = await client.get_tools()
    print("도구:", [t.name for t in tools])

asyncio.run(main())
# uv run python notebook/M2-도구에이전트/mcp_demo.py