from pydantic import BaseModel, Field
from enum import Enum

class SpecializedAgent(str, Enum):
    FINANCIAL_AGENT = "Financial Agent"
    SUMMARIZER_AGENT = "Summarizer Agent"
    CONVERSATIONAL_AGENT = "Conversational Agent"

class SupervisorResponse(BaseModel):
    delegated_agent: SpecializedAgent = Field(
        ...,
        description="The name of the specialized agent to which the task has been delegated",
        examples=r"{'delegated_agent': 'Financial Agent'}"
    )
    response_content: str = Field(
        ...,
        description="The response content from the delegated agent",
        examples=r"{'response_content': 'The stock price of XYZ Corp is currently $150.'}"
    )