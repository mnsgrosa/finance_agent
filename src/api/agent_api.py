from fastapi import FastAPI
from src.agent.agent_supervisor import agent_supervisor

app = FastAPI()
supervisor = agent_supervisor()

@app.post("/agent_input")
def agent_input(user_query: str):
    """
    Endpoint to receive user queries and process them through the agent supervisor.
    Args:
        user_query (str): The query from the user to be processed by the agent supervisor.
    Returns:
        dict: The response from the agent supervisor after processing the query.
    """
    output = supervisor.run_sync(user_query)
    