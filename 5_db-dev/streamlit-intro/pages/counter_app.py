import streamlit as st

st.title("Counter App")

if "count" not in st.session_state:
    st.session_state.count = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Reset"):
        st.session_state.count = 0
with col2:
    if st.button("Add"):
        st.session_state.count += 1
with col3:
    if st.button("Minus"):
        st.session_state.count -= 1
with col4:
    st.write(st.session_state.count)
