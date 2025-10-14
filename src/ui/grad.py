import gradio as gr
from app.src.agent.finance_agent import FinanceAgent

finance_agent = FinanceAgent()

def answer_agent(prompt: str) -> str:
    response = finance_agent.run(prompt)
    return response.content

gr.ChatInterface(
    fn = answer_agent,
    title = "Finance Agent",
    description = "An AI agent that can provide information about companies listed in the brazilian stock exchange (B3)",
    theme = "compact",
    type = "messages"
).launch()