"""18일차 완성본 — 사용자 상태와 개인화 UX.

오늘의 주제는 로그인 기능이 아니다. 백엔드의 로그인은 13일차에 이미 만들었다.
오늘 배우는 것은 **사용자 상태가 바뀔 때 화면이 어떻게 반응해야 하는가** 다.

    상태             조건                     화면
    -------------   ----------------------   --------------------------------
    비로그인         토큰 없음                 로그인 폼. 서비스가 뭔지도 알려줌
    로그인 + 빈 목록  연습 기록 0건             첫 면접을 시작하라는 안내
    로그인 + 선택 안함 목록은 있고 고르지 않음    무엇을 고르면 되는지
    로그인 + 내용 없음 대화는 있고 메시지 0건     예시 질문
    기본             주고받은 내용 있음         대화
    세션 만료         토큰이 60분을 넘김         왜 풀렸는지 + 다시 로그인

마지막 줄이 오늘 새로 생기는 상태다. 그리고 가장 많이 빠뜨리는 것이다.
"""

import streamlit as st

from common import (
    SERVICE_NAME,
    ApiError,
    SessionExpired,
    api,
    auth_headers,
    conversation_label,
)

st.set_page_config(page_title=SERVICE_NAME, layout="centered")

st.session_state.setdefault("access_token", None)
st.session_state.setdefault("user_email", None)
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("pending_question", None)
# 세션이 풀린 이유를 다음 실행에서 보여주려고 남겨둔다.
# 토큰만 지우고 끝내면 사용자는 자기가 왜 로그아웃됐는지 모른다.
st.session_state.setdefault("expired_notice", None)

EXAMPLE_QUESTIONS = [
    "면접을 시작해 주세요.",
    "1분 자기소개를 해보겠습니다.",
    "제 이력서에서 가장 많이 받을 질문이 뭘까요?",
]


def sign_out(notice: str | None = None) -> None:
    """로그인 관련 상태를 한 번에 지운다.

    지울 것을 빠뜨리면 다음 사용자에게 앞사람의 대화가 잠깐 보인다.
    그래서 로그아웃과 세션 만료가 같은 함수를 쓰게 해둔다.
    """
    st.session_state.access_token = None
    st.session_state.user_email = None
    st.session_state.conversation_id = None
    st.session_state.pending_question = None
    st.session_state.expired_notice = notice
    st.rerun()


@st.cache_data(ttl=300)
def load_options() -> dict:
    return api("GET", "/chat/options")


def render_login() -> None:
    """비로그인 상태의 화면 전체."""
    if st.session_state.expired_notice:
        st.warning(st.session_state.expired_notice)

    st.write("직무를 정하고 면접 질문에 답하며 연습합니다. 기록은 계정에 저장됩니다.")

    email = st.text_input("이메일", placeholder="you@example.com")
    password = st.text_input("비밀번호", type="password")

    login_column, signup_column = st.columns(2)
    action = None
    if login_column.button("로그인", use_container_width=True):
        action = "login"
    if signup_column.button("회원가입", use_container_width=True):
        action = "signup"

    if not action:
        return
    if not email or not password:
        st.error("이메일과 비밀번호를 모두 입력하세요.")
        return

    try:
        print(f"/auth/{action}")
        result = api(
            "POST",
            f"/auth/{action}",
            json={"email": email, "password": password},
        )
    except ApiError as error:
        st.error(str(error))
        return

    if not result.get("access_token"):
        # 가입은 됐는데 토큰이 없는 경우가 있다 (이메일 확인이 켜져 있을 때).
        st.error("가입은 되었지만 바로 로그인되지 않았습니다. 강사에게 알리세요.")
        return

    st.session_state.access_token = result["access_token"]
    st.session_state.user_email = result["email"]
    st.session_state.expired_notice = None
    st.rerun()


# 시그니처에 conversations를 추가합니다.(18일차)
def render_sidebar(options: dict, conversations: list) -> None:
    with st.sidebar:
        # 로그인이 된 상태 - 세션에 유저 이메일이 있음.
        st.caption(st.session_state.user_email)
        if st.button("로그아웃", use_container_width=True):
            sign_out()

        st.divider()
        st.subheader("연습 기록")

        if conversations:
            labels = {c["id"]: conversation_label(c) for c in conversations}
            ids = list(labels)
            current = st.session_state.conversation_id
            selected = st.selectbox(
                "지난 연습",
                options=ids,
                format_func=lambda cid: labels[cid],
                index=ids.index(current) if current in ids else 0,
                key="conversation_select",
            )
            st.session_state.conversation_id = selected

            new_title = st.text_input("새 이름", key="rename_input")
            rename_column, delete_column = st.columns(2)
            if (
                rename_column.button("이름 변경", use_container_width=True)
                and new_title
            ):
                api(
                    "PATCH",
                    f"/me/conversations/{selected}",
                    json={"title": new_title},
                    headers=auth_headers(),
                )
                st.rerun()
            if delete_column.button("삭제", use_container_width=True):
                api("DELETE", f"/me/conversations/{selected}", headers=auth_headers())
                st.session_state.conversation_id = None
                st.rerun()
        else:
            st.caption("아직 연습 기록이 없습니다.")

        st.divider()
        job_title = st.text_input("직무", placeholder="예: 백엔드 개발자")
        if st.button("새 면접 시작", use_container_width=True) and job_title:
            # 주의: user_id 를 보내지 않는다. 서버가 토큰에서 꺼내 쓴다.
            created = api(
                "POST",
                "/me/conversations",
                json={"title": job_title},
                headers=auth_headers(),
            )
            st.session_state.conversation_id = created["id"]
            st.rerun()

        st.divider()
        st.subheader("면접관 설정")
        st.radio("말투", options["tones"], key="tone", horizontal=True)
        st.radio("답변 길이", options["lengths"], key="length", horizontal=True)
        st.caption("고른 값은 다음 질문부터 적용됩니다.")


def render_empty(message: str, hint: str) -> None:
    st.info(message)
    st.caption(hint)


def ask(conversation_id: str, question: str) -> None:
    with st.spinner("면접관이 답변을 준비하는 중..."):
        api(
            "POST",
            f"/conversations/{conversation_id}/chat",
            json={
                "content": question,
                "tone": st.session_state.tone,
                "length": st.session_state.length,
            },
        )
    st.rerun()


def render_examples() -> None:
    st.caption("이렇게 시작해 보세요")
    columns = st.columns(len(EXAMPLE_QUESTIONS))
    for column, question in zip(columns, EXAMPLE_QUESTIONS):
        if column.button(question, use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()


def render_follow_ups(last_answer: str) -> None:
    st.caption("이어서")
    actions = {
        "더 자세히": f"방금 한 이 말을 예시를 들어 더 자세히 설명해 주세요.\n\n{last_answer}",
        "간단하게": f"방금 한 이 말을 세 문장으로 줄여 주세요.\n\n{last_answer}",
        "다음 질문": "다음 면접 질문을 하나 주세요.",
    }
    columns = st.columns(len(actions))
    for column, (label, question) in zip(columns, actions.items()):
        if column.button(label, use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()


def render_conversation(conversation_id: str) -> None:
    messages = api("GET", f"/conversations/{conversation_id}/messages")

    if not messages:
        render_empty(
            "아직 주고받은 내용이 없습니다.",
            "아래 예시를 누르거나 직접 입력해서 면접을 시작하세요.",
        )
        render_examples()

    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if messages and messages[-1]["role"] == "assistant":
        render_follow_ups(messages[-1]["content"])

    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        ask(conversation_id, question)

    if answer := st.chat_input("답변을 입력하세요"):
        ask(conversation_id, answer)


def render_signed_in() -> None:
    """로그인한 뒤의 화면 전체.

    이 안에서 나는 SessionExpired 는 아래 main 이 한 번에 받는다.
    호출마다 try 를 쓰면 스무 군데가 되고, 한 곳만 빠뜨려도
    거기서 화면이 비어 보인다.
    """
    options = load_options()
    st.session_state.setdefault("tone", options["default_tone"])
    st.session_state.setdefault("length", options["default_length"])

    conversations = api("GET", "/me/conversations", headers=auth_headers())
    render_sidebar(options, conversations)

    st.caption(f"말투 {st.session_state.tone} · 길이 {st.session_state.length}")

    if not conversations:
        render_empty(
            "아직 연습 기록이 없습니다.",
            "왼쪽에서 지원할 직무를 적고 `새 면접 시작` 을 누르세요.",
        )
    # 방어 가지. selectbox 가 첫 항목을 자동으로 고르므로 평소에는 닿지 않는다.
    # 목록이 있는데 선택이 비면 render_conversation(None) 이 되어 422 가 난다.
    elif not st.session_state.conversation_id:
        render_empty(
            "연습할 면접을 고르세요.",
            "왼쪽 `지난 연습` 에서 하나를 선택하면 됩니다.",
        )
    else:
        render_conversation(st.session_state.conversation_id)


st.title(SERVICE_NAME)

try:
    if st.session_state.access_token:
        render_signed_in()
    else:
        render_login()
except SessionExpired as error:
    # 토큰을 지우고 로그인 화면으로 돌린다. 이유는 다음 실행에서 보여준다.
    sign_out(str(error))
except ApiError as error:
    st.error(str(error))
