"""3과목 실습 환경 점검: uv run python verify_env.py"""

import os
import sys

from dotenv import load_dotenv


def check(name, fn):
    try:
        result = fn()
        suffix = f" - {result}" if result else ""
        print(f"  [OK] {name}{suffix}")
    except Exception as exc:
        print(f"  [FAIL] {name}: {exc}")


def check_import(module):
    """모듈을 불러오기만 한다. 성공하면 [OK]만 출력한다."""
    check(module, lambda: __import__(module) and None)


def mask_secret(value):
    if not value:
        return ""
    if len(value) <= 12:
        return "*" * len(value)
    return f"{value[:7]}...{value[-4:]}"


def check_openai_api_key():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env")
    if api_key.strip() in {"...", "sk-..."}:
        raise RuntimeError("OPENAI_API_KEY still looks like a placeholder")

    client = OpenAI(api_key=api_key)
    models = client.models.list()
    first_model = models.data[0].id if models.data else "no models returned"
    return f"authenticated, first model: {first_model}"


# 시스템 환경변수에 예전 키가 남아 있어도 .env 값을 우선한다
load_dotenv(override=True)

print(f"\nPython: {sys.version}")
print("-" * 45)

print("[Environment]")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"  OPENAI_API_KEY={mask_secret(openai_key) if openai_key else '(missing)'}")

# 확장 실습에만 쓰는 키 — 값은 출력하지 않고 있는지만 본다
print("\n[Optional keys for extension labs]")
for name in ["TAVILY_API_KEY", "LANGSMITH_API_KEY", "DATABASE_URL"]:
    print(f"  {name}={'(set)' if os.getenv(name) else '(missing - fill in before that lab)'}")

print("\n[Agent frameworks - M1]")
check_import("langchain")
check_import("langchain_openai")
check_import("langgraph")
check_import("langchain_mcp_adapters")
check_import("pydantic")

print("\n[Service and dashboard - M2, M3]")
check_import("fastapi")
check_import("uvicorn")
check_import("httpx")
check_import("tenacity")
check_import("streamlit")
check_import("psycopg2")

print("\n[Utilities]")
check_import("dotenv")
check_import("pandas")
check_import("ipykernel")
check_import("pytest")

print("\n[API]")
check("OpenAI API key", check_openai_api_key)

print("\nVerification complete.")
