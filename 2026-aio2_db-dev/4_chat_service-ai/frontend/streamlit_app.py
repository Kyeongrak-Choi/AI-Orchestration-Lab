import streamlit as st

from common import SERVICE_NAME, ApiError, api, conversation_label

st.set_page_config(page_title=SERVICE_NAME, layout="centered")

# 화면을 다시 그려도 유지해야 하는 값들. 여기서 한 번에 초기화한다.
st.session_state.setdefault("user_id", "")
st.session_state.setdefault("conversation_id", None)
st.session_state.setdefault("tone", "친절하게")
st.session_state.setdefault("length", "보통")
st.session_state.setdefault("pending_question", None)

EXAMPLE_QUESTIONS = [
    "면접을 시작해 주세요.",
    "1분 자기소개를 해보겠습니다.",
    "제 이력서에서 가장 많이 받을 질문이 뭘까요?",
]


@st.cache_data(ttl=300)
def load_options() -> dict:
    """선택지는 백엔드에서 받아온다.

    화면에 목록을 직접 적어두면 백엔드의 표와 두 곳에서 관리하게 된다.
    한쪽에 톤을 추가하고 다른 쪽을 잊으면, 버튼은 있는데 아무 효과가 없다.
    """
    return api("GET", "/chat/options")


def render_sidebar(options: dict) -> None:
    """왼쪽: 내가 누구인지 + 어떤 면접을 볼지 고르는 곳."""
    with st.sidebar:
        st.subheader("연습 기록")

        # 주의: 로그인은 18일차에 붙인다. 그때까지는 user_id 를 직접 입력해서 대신한다.
        st.session_state.user_id = st.text_input(
            "user_id (profiles.id)", st.session_state.user_id
        )

        if not st.session_state.user_id:
            st.caption("user_id 를 입력하면 연습 기록이 나타납니다.")
            return

        try:
            conversations = api(
                "GET", "/conversations", params={"user_id": st.session_state.user_id}
            )
        except ApiError as error:
            st.error(str(error))
            return

        if conversations:
            labels = {c["id"]: conversation_label(c) for c in conversations}
            ids = list(labels)
            # 주의: index 와 key 를 지정하지 않으면 화면을 다시 그릴 때 선택이 풀린다.
            current = st.session_state.conversation_id
            selected = st.selectbox(
                "지난 연습",
                options=ids,
                format_func=lambda cid: labels[cid],
                index=ids.index(current) if current in ids else 0,
                key="conversation_select",
            )
            st.session_state.conversation_id = selected
        else:
            st.caption("아직 연습 기록이 없습니다.")

        st.divider()
        job_title = st.text_input("직무", placeholder="예: 백엔드 개발자")
        if st.button("새 면접 시작", use_container_width=True) and job_title:
            try:
                created = api(
                    "POST",
                    "/conversations",
                    json={"user_id": st.session_state.user_id, "title": job_title},
                )
            except ApiError as error:
                st.error(str(error))
                return
            st.session_state.conversation_id = created["id"]
            st.rerun()

        # 면접관 설정 영역
        st.divider()
        st.subheader("면접관 설정")
        # 이 두 값이 곧 프롬프트의 두 문장이 된다.
        st.radio("말투", options["tones"], key="tone", horizontal=True)
        st.radio("답변 길이", options["lengths"], key="length", horizontal=True)
        st.caption(
            "고른 값은 다음 질문부터 적용됩니다. 이미 받은 답변은 바뀌지 않습니다."
        )


def render_empty(message: str, hint: str) -> None:
    """빈 화면은 "없다"가 아니라 "다음에 무엇을 하면 되는지"를 말해야 한다."""
    st.info(message)
    st.caption(hint)


def render_conversation(conversation_id: str) -> None:
    """가운데: 주고받은 내용과 입력칸."""
    try:
        messages = api("GET", f"/conversations/{conversation_id}/messages")
    except ApiError as error:
        st.error(str(error))
        return

    if not messages:
        render_empty(
            "아직 주고받은 내용이 없습니다.",
            "아래 입력칸에 첫 답변을 적어보세요. 오늘은 저장만 되고, 면접관의 질문은 17일차에 붙입니다.",
        )
        render_examples(conversation_id)

    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if messages and messages[-1]["role"] == "assistant":
        render_follow_ups(messages[-1]["content"])

    if answer := st.chat_input("답변을 입력하세요"):
        # try:
        #     api(
        #         "POST",
        #         f"/conversations/{conversation_id}/messages",
        #         json={"role": "user", "content": answer},
        #     )
        # except ApiError as error:
        #     st.error(str(error))
        #     return
        # st.rerun()
        ask(conversation_id, answer)

    # 버튼이 담아둔 질문이 있으면 먼저 보낸다.
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        ask(conversation_id, question)


def render_examples(conversation_id: str) -> None:
    """무엇을 물어야 할지 모르는 사람을 위한 출발점.

    빈 입력칸만 놓아두면 대부분 아무것도 입력하지 않고 나간다.
    """
    st.caption("이렇게 시작해 보세요")
    columns = st.columns(len(EXAMPLE_QUESTIONS))
    for column, question in zip(columns, EXAMPLE_QUESTIONS):
        if column.button(question, use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()


def ask(conversation_id: str, question: str) -> None:
    """질문을 보내고 답을 받는다. 실패하면 화면에 이유를 남긴다."""
    try:
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
    except ApiError as error:
        st.error(str(error))
        return
    st.rerun()


def render_follow_ups(last_answer: str) -> None:
    """직전 답변을 두고 이어서 할 수 있는 행동.

    주의: 오늘은 모델이 이전 대화를 기억하지 못한다(19일차 주제).
    그래서 직전 답변을 질문 안에 넣어서 보낸다. 맥락은 결국 프롬프트로 들어간다.
    """
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


try:
    options = load_options()
except ApiError as error:
    st.title(SERVICE_NAME)
    st.error(str(error))
    st.stop()

# 라디오 버튼의 초기값. 백엔드가 알려준 기본값을 쓴다.
st.session_state.setdefault("tone", options["default_tone"])
st.session_state.setdefault("length", options["default_length"])


render_sidebar(options)

st.title(SERVICE_NAME)
st.caption("직무를 정하고 면접 질문에 답하며 연습합니다. 오늘은 화면만 만듭니다.")

if not st.session_state.user_id:
    render_empty(
        "왼쪽에 user_id 를 입력하세요.",
        "Supabase SQL Editor 에서 `select id, username from profiles;` 로 확인할 수 있습니다.",
    )
elif not st.session_state.conversation_id:
    render_empty(
        "연습할 면접을 고르거나 새로 시작하세요.",
        "왼쪽에서 직무를 적고 `새 면접 시작` 을 누르면 됩니다.",
    )
else:
    render_conversation(st.session_state.conversation_id)


# st.title(SERVICE_NAME)
# st.caption(f"말투 {st.session_state.tone} · 길이 {st.session_state.length}")
