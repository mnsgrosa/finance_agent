import streamlit as st
import httpx
import pandas as pd

if "history" not in st.session_state:
    st.session_state["history"] = []

@st.cache_resource
def textual_output(text):
    st.session_state["history"].append({
        "role": "agent", 
        "content": text,
        "figure": None
    })
    st.markdown(text)

@st.cache_resource
def data_points(response):
    x = []
    y = []

    for point in response.get("points", []):
        x.append(point["date"])
        y.append(point["value"])

    df = pd.DataFrame({"Date": x, "Value": y})
    figure = st.line_chart(df, x = "Date", y = "Value")
    st.session_state["history"].append({
        "role": "agent", 
        "content": "Here is the requested data plot:",
        "figure": figure
    })
    return figure

@st.cache_resource
def summary_text(response):
    headline = response.get("headline", "")
    summary = response.get("summary", "")
    full_summary = f"**{headline}**\n\n{summary}"
    st.session_state["history"].append({
        "role": "agent", 
        "content": full_summary,
        "figure": None
    })
    st.markdown(full_summary)

if "responses" not in st.session_state:
    st.session_state["responses"] = {
        "ticker": textual_output,
        "content": textual_output,
        "points": data_points,
        "summary": summary_text
    }

for message in st.session_state["history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state["history"]:
    for message in st.session_state["history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["figure"]:
                st.line_chart(message["figure"])

if prompt := st.chat_input("Ask me about stocks and companies!"):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["history"].append({"role": "user", "content": prompt})
    response = httpx.post("http://localhost:8000/agent_input", json = {"user_query": prompt})
    
    if response.status_code != 200:
        st.error("Error communicating with the agent API.")
        st.stop()

    response_dict = response.json().get("content", {})

    ticker = response_dict.get("ticker", None)
    points = response_dict.get("points", None)
    headline = response_dict.get("headline", None)
    summary = response_dict.get("summary", None)
    content = response_dict.get("content", None)

    if ticker:
        st.session_state["responses"]["ticker"](f"The ticker symbol is: {ticker}")
    
    if points:
        st.session_state["responses"]["points"](response_dict)

    if headline or summary:
        st.session_state["responses"]["summary"](response_dict)

    if content:
        st.session_state["responses"]["content"](content)