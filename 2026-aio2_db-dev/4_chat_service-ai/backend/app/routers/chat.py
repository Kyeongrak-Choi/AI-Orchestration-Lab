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
from app.routers.conversations import create_message, list_messages
from app.schemas import ChatRequest, MessageCreate, MessageOut

router = APIRouter(prefix="/conversations", tags=["chat"])

# 선택지를 화면에 알려주는 라우터. 경로 모양이 달라 별도로 둔다.
options_router = APIRouter(prefix="/chat", tags=["chat"])

# 사용자와 면접관 메시지를 합쳐 최근 몇 개까지 모델에 보낼지.
# 20개면 대략 10번 주고받은 분량이다.
MAX_HISTORY_MESSAGES = 20

# 우리 DB 의 role 을 Gemini 의 role 로 바꾼다.
# 이 표에 없는 role(system)은 아예 보내지 않는다.
_ROLE_MAP = {"user": "user", "assistant": "model"}

# 맥락을 끊는 표시. 실제 메시지처럼 저장하지만 모델에는 보내지 않는다.
# 새 컬럼을 만들지 않고 기존 role 을 쓰는 이유는, 화면에 그대로 보여줘야 하기 때문이다.
# 사용자는 "여기서 끊었다"는 사실을 볼 수 있어야 한다.
CONTEXT_RESET_MARKER = "[맥락 초기화] 이 지점 이전은 면접관이 기억하지 않습니다."


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
        "max_history_messages": MAX_HISTORY_MESSAGES,
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


def _build_history(conversation_id: UUID) -> list[dict]:
    """모델에게 보낼 이전 대화를 만든다.

    세 단계로 줄인다. 순서가 중요하다.
      1) 마지막 초기화 지점 이후만 남긴다
      2) 모델이 모르는 role(system)을 뺀다
      3) 최근 MAX_HISTORY_MESSAGES 개만 남긴다

    3번을 1번보다 먼저 하면, 최근 20개 안에 초기화 지점이 없을 때
    끊었던 옛날 대화가 다시 딸려 들어간다.
    """
    messages = list_messages(conversation_id)  # 시간 오름차순, Redis 캐시 적용됨

    for index in range(len(messages) - 1, -1, -1):
        if messages[index]["role"] == "system":
            messages = messages[index + 1 :]
            break

    usable = [m for m in messages if m["role"] in _ROLE_MAP]
    recent = usable[-MAX_HISTORY_MESSAGES:]

    return [
        {"role": _ROLE_MAP[m["role"]], "parts": [{"text": m["content"]}]}
        for m in recent
    ]


@router.post("/{conversation_id}/reset-context", response_model=MessageOut)
def reset_context(conversation_id: UUID):
    """맥락을 끊는다. 기록은 지우지 않는다.

    주의: 메시지를 삭제하지 않는다. 사용자가 연습한 내용은 그대로 남아야 한다.
         지워지는 것은 "모델이 참고하는 범위"뿐이다.
    """
    return create_message(
        conversation_id, MessageCreate(role="system", content=CONTEXT_RESET_MARKER)
    )


@router.post("/{conversation_id}/chat", response_model=MessageOut)
def chat(conversation_id: UUID, payload: ChatRequest):
    job_title = _job_title(conversation_id)
    history = _build_history(conversation_id)

    # 1) 사용자 메시지를 먼저 저장한다.
    #    모델 호출이 실패해도(429 등) 사용자가 쓴 답변은 남아야 한다.
    create_message(conversation_id, MessageCreate(role="user", content=payload.content))

    contents = history + [{"role": "user", "parts": [{"text": payload.content}]}]

    # 제미나이 시스템 프롬프트를 생성한다.
    system_prompt = build_system_prompt(job_title, payload.tone, payload.length)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            # contents=payload.content,
            contents=contents,
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
            status_code=503,
            detail="모델이 빈 응답을 돌려주었습니다. 질문을 바꿔서 다시 시도하세요.",
        )

    return create_message(
        conversation_id, MessageCreate(role="assistant", content=response.text)
    )


@router.post("/{conversation_id}/reset-context", response_model=MessageOut)
def reset_context(conversation_id: UUID):
    """맥락을 끊는다. 기록은 지우지 않는다.

    주의: 메시지를 삭제하지 않는다. 사용자가 연습한 내용은 그대로 남아야 한다.
         지워지는 것은 "모델이 참고하는 범위"뿐이다.
    """
    return create_message(
        conversation_id, MessageCreate(role="system", content=CONTEXT_RESET_MARKER)
    )
