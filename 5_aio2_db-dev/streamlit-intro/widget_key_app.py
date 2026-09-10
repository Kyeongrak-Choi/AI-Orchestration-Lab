import streamlit as st

st.title("Widget key and Session State")

# 1. key 를 주면 입력한 값이 st.session_state["nickname"] 에 자동으로 담긴다.
st.text_input("nickname", key="nickname")

# 2. selectbox 는 보이는 글자와 실제 값을 다르게 둘 수 있다.
fruits = {"a": "apple", "b": "banana", "c": "cherry"}
st.selectbox(
    "choice favorite fluit",
    options=list(fruits),               # 실제 값은 a / b / c
    format_func=lambda key: fruits[key],  # 화면에 보이는 것은 사과 / 바나나 / 체리
    key="fruit",
)

st.divider()

# 3. 세션 상태에 무엇이 담겼는지 그대로 본다.
st.write("in session_state")
st.write(dict(st.session_state))