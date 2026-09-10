import pandas as pd
import streamlit as st

st.header("st.dataframe()")

df_simple = pd.DataFrame(
    {
        "fruit": ["apple", "banana", "peach", "grape"],
        "Price": ["3000", "1000", "2000", "5000"],
        "ea": [10, 5, 20, 9],
    }
)

st.dataframe(df_simple)
