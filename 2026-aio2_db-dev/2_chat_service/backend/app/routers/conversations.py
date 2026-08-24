"""대화·메시지 API (실습 6·7).

메서드   주소                                  하는 일                성공 코드
POST     /conversations                        대화 생성               201
GET      /conversations?user_id=               사용자별 대화 목록       200
POST     /conversations/{id}/messages          메시지 저장             201
GET      /conversations/{id}/messages          메시지 목록             200
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db import supabase
from app.schemas import ConversationCreate, ConversationOut, MessageCreate, MessageOut

# TODO 0. app.schemas 에서 ConversationCreate, ConversationOut,
#         MessageCreate, MessageOut 을 가져온다

router = APIRouter(prefix="/conversations", tags=["conversations"])


# ── 실습 6 ────────────────────────────────────────────────────────
# TODO 1. POST "" — 대화 생성
#   · insert 전에 users 에 그 user_id 가 있는지 확인한다.
#     DB의 외래키도 막아주지만 그대로 두면 500 이 난다. 먼저 확인해 404 로 알리는 편이 친절하다.
#   · 없으면 404 "사용자를 찾을 수 없습니다"


@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(conv_info: ConversationCreate):
    user = (
        supabase.table("users").select("id").eq("id", str(conv_info.user_id)).execute()
    )
    if not user.data:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    result = (
        supabase.table("conversations")
        .insert({"user_id": str(conv_info.user_id), "title": conv_info.title})
        .execute()
    )
    return result.data[0]


# TODO 2. GET "" — 사용자별 대화 목록
#   · user_id 는 주소 뒤 ?user_id=... 로 온다. 함수 인자에 그냥 적으면 된다.
#   · 기본값을 주지 않으면 필수가 되고, 빠뜨리면 FastAPI 가 422 로 막는다.
#   · 최신순 정렬


@router.get("", response_model=list[ConversationOut])
def list_conversations(user_id: UUID):
    result = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", str(user_id))
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


# ── 실습 7 ────────────────────────────────────────────────────────
# 주의: 정렬 방향이 대화와 반대다.
#       대화 목록은 최신순(desc=True)이지만,
#       메시지는 오래된 것부터(desc=False)여야 대화 흐름 그대로 읽힌다.

# TODO 3. POST "/{conversation_id}/messages" — 메시지 저장
#   · 대화가 없으면 404 "대화를 찾을 수 없습니다"


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
def create_message(conversation_id: UUID, payload: MessageCreate):
    conversation = (
        supabase.table("conversations")
        .select("id")
        .eq("id", str(conversation_id))
        .execute()
    )
    if not conversation.data:
        raise HTTPException(status_code=404, detail="Not found conversation")

    result = (
        supabase.table("messages")
        .insert(
            {
                "conversation_id": str(conversation_id),
                "role": payload.role,
                "content": payload.content,
            }
        )
        .execute()
    )
    return result.data[0]


# TODO 4. GET "/{conversation_id}/messages" — 메시지 목록
#   · 대화가 없으면 404
#   · .order("created_at", desc=False)


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(conversation_id: UUID):
    conversation = (
        supabase.table("conversations")
        .select("id")
        .eq("id", str(conversation_id))
        .execute()
    )
    if not conversation.data:
        raise HTTPException(status_code=404, detail="Not found conversation")

    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", str(conversation_id))
        .order("created_at", desc=False)
        .execute()
    )
    return result.data


# 연습문제1. 대화 제목 수정
@router.patch("/{conv_id}", response_model=ConversationOut)
def update_title(conv_id: UUID, conv_info: ConversationCreate):
    result = (
        supabase.table("conversations")
        .update({"title": conv_info.title})
        .eq("id", str(conv_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Not found conversation")
    return result.data[0]


# 연습문제 2. 대화 삭제
@router.delete("/{conv_id}", status_code=204)
def delete_user(id: UUID):
    result = supabase.table("conversations").delete().eq("id", str(id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Not found conversation")

# 연습문제 3. 이메일로 사용자 찾기



# 연습문제 4. 메시지 목록 페이지 나누기