from fastapi import FastAPI
from ..agent_supervisor import agent_supervisor
from .api_schema import ApiResponseSchema
import logfire

app = FastAPI()
supervisor = agent_supervisor()

logfire.configure(
    service_name = "agent_api_service",
)

logfire.instrument_fastapi(app)

@app.post("/agent_input", response_model = ApiResponseSchema)
def agent_input(user_query: str):
    """
    Endpoint to receive user queries and process them through the agent supervisor.
    Args:
        user_query (str): The query from the user to be processed by the agent supervisor.
    Returns:
        dict: The response from the agent supervisor after processing the query.
    """
    output = supervisor.run_sync(user_query)
    response = ApiResponseSchema(
        delegated_agent = output.delegated_agent,
        content = output.content
    )
    return response