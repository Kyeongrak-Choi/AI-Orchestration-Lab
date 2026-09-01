"""면접관 응답을 만드는 라우터.

오늘은 단발성이다. 이전 대화를 모델에 넘기지 않는다 (19일차에 붙인다).
스트리밍도 아직이다 (20일차). 질문 하나에 답 하나다.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from google.genai import types

from app.db import supabase
from app.gemini_client import (
    DEFAULT_LENGTH,
    DEFAULT_TONE,
    GEMINI_MODEL,
    LENGTHS,
    TONES,
    build_system_prompt,
    client,
)
from app.routers.conversations import create_message
from app.schemas import ChatRequest, MessageCreate, MessageOut

router = APIRouter(prefix="/conversations", tags=["chat"])

# 선택지를 화면에 알려주는 라우터. 경로 모양이 달라 별도로 둔다.
options_router = APIRouter(prefix="/chat", tags=["chat"])


@options_router.get("/options")
def chat_options():
    """화면이 그릴 선택지를 내려준다.
	
	채팅 옵션은 gemini_client.py 의 표에서만 관리한다.
    화면에 목록을 직접 적어두면 두 곳 모두에서 관리해야 한다.
    한쪽에 톤을 추가하고 다른 쪽을 잊으면, 버튼은 있는데 아무 효과가 없다.
    """
    return {
        "tones": list(TONES),
        "lengths": list(LENGTHS),
        "default_tone": DEFAULT_TONE,
        "default_length": DEFAULT_LENGTH,
    }


def _job_title(conversation_id: UUID) -> str:
    """대화 제목이 곧 지원 직무다. 16일차에 `새 면접 시작` 에서 받은 값이다."""
    result = (
        supabase.table("conversations")
        .select("title")
        .eq("id", str(conversation_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="conversation not found")
    return result.data[0]["title"] or "지원 직무 미지정"

@router.post("/{conversation_id}/chat", response_model=MessageOut)
def chat(conversation_id: UUID, payload: ChatRequest):
    job_title = _job_title(conversation_id)

    # 1) 사용자 메시지를 먼저 저장한다.
    #    모델 호출이 실패해도(429 등) 사용자가 쓴 답변은 남아야 한다.
    create_message(conversation_id, MessageCreate(role="user", content=payload.content))
	
	# 제미나이 시스템 프롬프트를 생성한다.
    system_prompt = build_system_prompt(job_title, payload.tone, payload.length)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=payload.content,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
    except Exception as e:
        # 감싸지 않으면 FastAPI 가 원인 없는 500 만 돌려준다.
        # 화면이 무엇 때문에 실패했는지 알 수 있어야 사용자에게 설명할 수 있다.
        raise HTTPException(
            status_code=503, detail=f"응답 생성 실패: {type(e).__name__}: {e}"
        )

    # 주의: 안전 필터에 걸리면 예외가 아니라 text 가 None 으로 온다.
    if not response.text:
        raise HTTPException(
            status_code=503, detail="모델이 빈 응답을 돌려주었습니다. 질문을 바꿔서 다시 시도하세요."
        )

    return create_message(
        conversation_id, MessageCreate(role="assistant", content=response.text)
    )