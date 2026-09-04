"""면접관 응답을 만드는 라우터.

19일차까지는 답이 다 만들어진 뒤에 한 번에 돌려줬다. 오늘은 **만들어지는 대로 흘려보낸다.**

SSE(Server-Sent Events)를 쓴다. 한 번의 응답을 여러 조각으로 나눠 보내는 방식이다.

    data: {"text": "안녕하세요"}
    data: {"text": ", 백엔드 개발자"}
    data: {"done": true, "message_id": "..."}

조각을 그냥 문자열로 보내지 않고 JSON 으로 감싼다. **답변 안에 줄바꿈이 있기 때문이다.**
SSE 는 빈 줄을 이벤트의 끝으로 약속하고 있어서, 줄바꿈을 그대로 흘리면 형식이 깨진다.

한 가지를 더 알아야 한다. **스트림이 시작되면 상태 코드를 바꿀 수 없다.**
헤더가 이미 나갔기 때문이다. 그래서 스트림 도중의 실패는 상태 코드가 아니라
error 이벤트로 알린다.
"""

import json
import time
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google.genai import types

from app.db import supabase
from app.deps import require_own_conversation
from app.gemini_client import (
    DEFAULT_LENGTH,
    DEFAULT_TONE,
    GEMINI_MODEL,
    LENGTHS,
    TONES,
    build_system_prompt,
    client,
)
from app.redis_client import r
from app.routers.conversations import create_message, list_messages
from app.schemas import (
    ChatRequest,
    FeedbackRequest,
    MessageCreate,
    MessageOut,
    RegenerateRequest,
)

router = APIRouter(prefix="/conversations", tags=["chat"])
options_router = APIRouter(prefix="/chat", tags=["chat"])

MAX_HISTORY_MESSAGES = 20
MAX_USAGE_LOGS = 50

CONTEXT_RESET_MARKER = "[맥락 초기화] 이 지점 이전은 면접관이 기억하지 않습니다."

# 우리 DB 의 role 을 Gemini 의 role 로 바꾼다.
# 주의: assistant 를 그대로 보내도 지금은 통과한다. 그러나 서버가 인정한다고
#      말하는 값은 MODEL 과 USER 뿐이고(다른 값은 400), 별칭은 문서에 없다.
_ROLE_MAP = {"user": "user", "assistant": "model"}


@options_router.get("/options")
def chat_options():
    return {
        "tones": list(TONES),
        "lengths": list(LENGTHS),
        "default_tone": DEFAULT_TONE,
        "default_length": DEFAULT_LENGTH,
        "max_history_messages": MAX_HISTORY_MESSAGES,
    }


def _job_title(conversation_id: UUID) -> str:
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
    """모델에게 보낼 이전 대화를 만든다. 순서가 중요하다 (19일차 참고)."""
    messages = list_messages(conversation_id)

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


# ---------------------------------------------------------------- 로그와 피드백


def _usage_log_key(conversation_id: UUID) -> str:
    return f"usage_log:{conversation_id}"


def _feedback_key(conversation_id: UUID) -> str:
    return f"feedback:{conversation_id}"


def _log_usage(conversation_id: UUID, started_at: float, usage) -> None:
    """언제 요청했고 얼마나 걸렸는지 남긴다.

    Redis 리스트에 넣고 최근 N건만 남긴다. 새 테이블을 만들지 않는 이유는
    이것이 서비스 데이터가 아니라 운영 기록이기 때문이다. 지워져도 서비스는 돈다.
    """
    entry = {
        "requested_at": datetime.now(UTC).isoformat(),
        "latency_ms": round((time.monotonic() - started_at) * 1000),
        "prompt_tokens": getattr(usage, "prompt_token_count", None),
        "response_tokens": getattr(usage, "candidates_token_count", None),
        "total_tokens": getattr(usage, "total_token_count", None),
    }
    key = _usage_log_key(conversation_id)
    r.lpush(key, json.dumps(entry))
    r.ltrim(key, 0, MAX_USAGE_LOGS - 1)


@router.post("/{conversation_id}/feedback")
def save_feedback(
    payload: FeedbackRequest,
    conversation_id: UUID = Depends(require_own_conversation),
):
    """어떤 답변이 도움이 됐는지 기록한다.

    메시지 하나에 값 하나라서 리스트가 아니라 해시를 쓴다.
    같은 메시지에 다시 누르면 덮어써야 하기 때문이다.
    """
    key = _feedback_key(conversation_id)
    if payload.value is None:
        r.hdel(key, str(payload.message_id))  # 취소
    else:
        r.hset(key, str(payload.message_id), payload.value)
    return {"message_id": str(payload.message_id), "value": payload.value}


@router.get("/{conversation_id}/feedback")
def read_feedback(conversation_id: UUID = Depends(require_own_conversation)):
    """화면이 버튼의 눌린 상태를 그릴 수 있게 전부 돌려준다."""
    return r.hgetall(_feedback_key(conversation_id))


@router.get("/{conversation_id}/usage-logs")
def usage_logs(conversation_id: UUID = Depends(require_own_conversation)):
    raw = r.lrange(_usage_log_key(conversation_id), 0, MAX_USAGE_LOGS - 1)
    return [json.loads(item) for item in raw]


@router.post("/{conversation_id}/reset-context", response_model=MessageOut)
def reset_context(conversation_id: UUID = Depends(require_own_conversation)):
    """맥락을 끊는다. 기록은 지우지 않는다 (19일차 참고).

    인증을 요구하지 않는다. 같은 라우터의 /chat, /messages 와 맞춘 것이다.
    셋 다 21일차에 함께 막는다. 여기만 막으면 규칙이 뒤죽박죽이 된다.
    """
    return create_message(
        conversation_id, MessageCreate(role="system", content=CONTEXT_RESET_MARKER)
    )


# ---------------------------------------------------------------- 응답 생성


def _stream_answer(conversation_id: UUID, contents: list, system_prompt: str):
    """모델의 응답을 조각으로 흘려보내고, 끝나면 통째로 저장한다."""

    def event_stream():
        started_at = time.monotonic()
        full_text = ""
        last_usage = None
        try:
            for chunk in client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system_prompt),
            ):
                if chunk.text:
                    full_text += chunk.text
                    # 주의: 조각 안의 줄바꿈은 그대로 보내면 SSE 형식이 깨진다.
                    #      한 이벤트는 빈 줄로 끝나기로 약속돼 있기 때문이다.
                    yield "data: " + json.dumps({"text": chunk.text}) + "\n\n"
                if chunk.usage_metadata:
                    last_usage = chunk.usage_metadata
        except Exception as e:
            # 스트림이 이미 시작돼 상태 코드를 바꿀 수 없다. 이벤트로 알린다.
            yield "data: " + json.dumps({"error": f"{type(e).__name__}: {e}"}) + "\n\n"
            return

        if not full_text:
            yield (
                "data: "
                + json.dumps({"error": "모델이 빈 응답을 돌려주었습니다."})
                + "\n\n"
            )
            return

        # 다 받은 뒤에 한 번만 저장한다. 조각마다 저장하면 메시지가 수십 개로 쪼개진다.
        saved = create_message(
            conversation_id, MessageCreate(role="assistant", content=full_text)
        )
        _log_usage(conversation_id, started_at, last_usage)
        yield "data: " + json.dumps({"done": True, "message_id": saved["id"]}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/{conversation_id}/chat")
def chat(
    payload: ChatRequest, conversation_id: UUID = Depends(require_own_conversation)
):
    job_title = _job_title(conversation_id)

    # 스트리밍을 시작하기 전에 끝내둔다. 제너레이터 안에 두면
    # 클라이언트가 스트림을 끝까지 안 받았을 때 저장이 안 될 수 있다.
    history = _build_history(conversation_id)
    create_message(conversation_id, MessageCreate(role="user", content=payload.content))

    contents = history + [{"role": "user", "parts": [{"text": payload.content}]}]
    return _stream_answer(
        conversation_id,
        contents,
        build_system_prompt(job_title, payload.tone, payload.length),
    )


@router.post("/{conversation_id}/regenerate")
def regenerate(
    payload: RegenerateRequest,
    conversation_id: UUID = Depends(require_own_conversation),
):
    """마지막 답변을 지우고 다시 만든다.

    Retry 와 다르다. Retry 는 실패한 요청을 그대로 다시 보내는 것이고,
    Regenerate 는 **성공한 답변이 마음에 안 들 때** 새로 받는 것이다.
    그래서 여기서는 마지막 assistant 메시지를 지우는 일이 먼저다.
    """
    messages = list_messages(conversation_id)
    if not messages or messages[-1]["role"] != "assistant":
        raise HTTPException(status_code=400, detail="다시 생성할 답변이 없습니다.")

    supabase.table("messages").delete().eq("id", messages[-1]["id"]).execute()
    r.delete(f"messages:{conversation_id}")  # 캐시를 지워야 방금 삭제가 반영된다

    job_title = _job_title(conversation_id)
    history = _build_history(
        conversation_id
    )  # 삭제 후라 마지막 사용자 질문까지만 들어온다
    if not history:
        raise HTTPException(status_code=400, detail="다시 생성할 질문이 없습니다.")

    return _stream_answer(
        conversation_id,
        history,
        build_system_prompt(job_title, payload.tone, payload.length),
    )
