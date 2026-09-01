import streamlit as st

st.title("Fist Streamlit Application")

st.write("Hi Streamlit")
st.write("This is Simple App made by Streamlit")

st.header("header")
st.markdown("""
## markdown String 
- 1
- 2
- 3
- 4
""")

# st.success("Success")
# st.area_chart("area_chart")
# st.balloons("ballonns")
# st.code("code")


st.page_link("pages/counter_app.py", label="Click", icon="⚙️")
