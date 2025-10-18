import streamlit as st
from src.agent.finance_agent import FinanceAgent

@st.cache_resource
def get_agent():
    return FinanceAgent()

if "agent" not in st.session_state:
    st.session_state["agent"] = get_agent()

if "history" not in st.session_state:
    st.session_state["history"] = []

for message in st.session_state["history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask me about stocks and companies!"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["history"].append({"role": "user", "content": prompt})

    response = st.session_state["agent"].run(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.content)