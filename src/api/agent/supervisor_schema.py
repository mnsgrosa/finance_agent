from pydantic import BaseModel, Field
from typing import Dict, Any

class SupervisorResponse(BaseModel):
    delegated_agent: SpecializedAgent = Field(
        ...,
        description = "The name of the specialized agent to which the task has been delegated",
        examples = "Financial agent, Summarizer agent, Conversational agent"
    )
    content: Dict[str, Any] = Field(
        ...,
        description = "The response content from the delegated agent, it can vary based on the agent's functionality",
        examples = r"'The stock price of XYZ Corp is currently $150.' or [{'2025-01-01: 150.0}, {'2025-01-02: 152.5}]'"
    )