"""10일차 — LLM 호출을 FastAPI로 감싸기.

노트북 05에서 셀 단위로 만들어본 것을, 여기에 하나의 파일로 옮겨 담는다.
DB도 인증도 대화 이력도 없다 — 그건 12·13·17일차에서 차례로 붙인다.

실행:
    uv run uvicorn app:app --reload
    브라우저에서 http://127.0.0.1:8000/docs
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# override=True: 서버가 이미 떠 있으면 os.environ의 옛 키가 남아 있고,
# 기본값(False)으로는 .env가 그걸 덮어쓰지 못해 키를 고쳐도 인증 오류가 계속 난다.
load_dotenv(override=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"

app = FastAPI(title="llm-api-basic", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    # TODO: temperature 를 추가한다. 기본값 0.7, 허용 범위는 노트북 03에서 확인한 값으로 제한한다
    # TODO: max_output_tokens 를 추가한다. 기본값 256, 1 이상 2048 이하
    # TODO: system_instruction 을 추가한다. 없어도 되는 값이다


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class AskResponse(BaseModel):
    answer: str
    model: str
    usage: Usage


@app.get("/health")
def health():
    """서버가 살아있는지 확인. 키 값 자체는 절대 돌려주지 않는다."""
    return {"status": "ok", "model": MODEL, "key_loaded": bool(os.getenv("GEMINI_API_KEY"))}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """질문 하나를 받아 Gemini 응답과 토큰 사용량을 함께 돌려준다."""
    config = types.GenerateContentConfig(
        # TODO: req 의 temperature / max_output_tokens / system_instruction 을 넘긴다
    )
    try:
        r = client.models.generate_content(model=MODEL, contents=req.question, config=config)
    except Exception as e:
        # TODO: 429 / 503 처럼 일시적인 오류는 클라이언트에 503 으로 내려준다.
        #       우리 코드의 버그가 아니므로 500 을 쓰지 않는다 (노트북 02 참고)
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {str(e)[:200]}") from e

    u = r.usage_metadata
    return AskResponse(
        answer=r.text or "",
        model=r.model_version,
        # TODO: usage_metadata 의 세 값을 Usage 에 담는다
        #       Gemini 쪽 이름과 우리 API 의 이름이 다르다 — 무엇이 무엇에 대응하는지 확인할 것
        usage=Usage(input_tokens=0, output_tokens=0, total_tokens=0),
    )
