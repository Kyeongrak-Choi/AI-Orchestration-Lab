"""로그인한 사용자 본인에 대한 엔드포인트.

여기 있는 모든 함수의 공통점은 **user_id 를 요청에서 받지 않는다**는 것이다.
토큰에서 꺼낸 current_user.id 만 신뢰한다. 요청 body 를 믿으면
아무나 남의 user_id 를 적어 보낼 수 있다.

수정·삭제는 우리가 직접 소유권을 검사하지 않는다. RLS 가 DB 에서 막는다.
내 것이 아니면 0건이 바뀌고, 그것을 404 로 돌려준다.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.db import get_anon_client
from app.deps import CurrentUser, get_current_user
from app.schemas import ConversationOut, ConversationUpdate, MyConversationCreate

router = APIRouter(prefix="/me", tags=["me"])


@router.get("")
def read_me(current_user: CurrentUser = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}


@router.get("/conversations", response_model=list[ConversationOut])
def my_conversations(current_user: CurrentUser = Depends(get_current_user)):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    # where 절에 user_id 가 없는 것에 주목한다. RLS 가 알아서 내 것만 준다.
    result = (
        client.table("conversations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.post("/conversations", response_model=ConversationOut)
def create_my_conversation(
    payload: MyConversationCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    result = (
        client.table("conversations")
        .insert({"user_id": current_user.id, "title": payload.title})
        .execute()
    )
    return result.data[0]


@router.patch("/conversations/{conversation_id}", response_model=ConversationOut)
def rename_my_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    result = (
        client.table("conversations")
        .update({"title": payload.title})
        .eq("id", str(conversation_id))
        .execute()
    )
    if not result.data:
        # 없는 대화와 남의 대화를 구분하지 않고 똑같이 404 로 답한다.
        # 구분해서 알려주면 "그 대화는 존재한다"는 정보를 흘리게 된다.
        raise HTTPException(status_code=404, detail="conversation not found")
    return result.data[0]


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_my_conversation(
    conversation_id: UUID, current_user: CurrentUser = Depends(get_current_user)
):
    client = get_anon_client()
    client.postgrest.auth(current_user.token)
    result = (
        client.table("conversations").delete().eq("id", str(conversation_id)).execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="conversation not found")