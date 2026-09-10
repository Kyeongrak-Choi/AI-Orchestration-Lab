from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    user_id: UUID
    title: str | None = None


class ConversationOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime


class MyConversationCreate(BaseModel):
    # 주의: user_id 를 받지 않는다. 토큰에서 꺼낸 값만 신뢰한다.
    #      받으면 남의 명의로 대화를 만들 수 있다.
    title: str | None = None


class ConversationUpdate(BaseModel):
    title: str


class ChatRequest(BaseModel):
    content: str
    # 화면에서 고른 값. 안 보내면 None 이고, gemini_client 가 기본값으로 바꾼다.
    # 주의: 여기에 기본 문자열을 적지 않는다. 적으면 선택지 목록이 두 파일에 나뉘어
    #      한쪽만 고쳤을 때 어긋난다. 선택지는 gemini_client.py 한 곳에만 둔다.
    tone: str | None = None
    length: str | None = None


class RegenerateRequest(BaseModel):
    # 주의: ChatRequest 를 재사용하면 안 된다. 거기에는 content 가 필수라서,
    #      질문을 다시 보내지 않는 이 요청은 422 로 거부당한다.
    tone: str | None = None
    length: str | None = None


class FeedbackRequest(BaseModel):
    message_id: UUID
    # None 이면 취소다. 한 번 누른 것을 되돌릴 수 있어야 한다.
    value: Literal["up", "down"] | None = None


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str | None
    user_id: str
    email: str