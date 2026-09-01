import streamlit as st

from common import ApiError, SERVICE_NAME, api, conversation_label

st.set_page_config(page_title=SERVICE_NAME, layout="centered")

# 화면을 다시 그려도 유지해야 하는 값들. 여기서 한 번에 초기화한다.
st.session_state.setdefault("user_id", "")
st.session_state.setdefault("conversation_id", None)


def render_sidebar() -> None:
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

    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if answer := st.chat_input("답변을 입력하세요"):
        try:
            api(
                "POST",
                f"/conversations/{conversation_id}/messages",
                json={"role": "user", "content": answer},
            )
        except ApiError as error:
            st.error(str(error))
            return
        st.rerun()

render_sidebar()

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