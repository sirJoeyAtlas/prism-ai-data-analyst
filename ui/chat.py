import streamlit as st
from database import db


def render_chat_history(dataset_id: int):
    history = db.get_queries(dataset_id)
    for q in reversed(history):
        with st.chat_message("user", avatar="❓"):
            st.markdown(q["question"])
        with st.chat_message("assistant", avatar="📊"):
            if q["explanation"]:
                st.markdown(q["explanation"])
            with st.expander("View generated code"):
                st.code(q["generated_code"] or "", language="python")