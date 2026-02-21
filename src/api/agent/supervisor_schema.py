from pydantic import BaseModel, Field
from typing import Dict, Any

class SupervisorResponse(BaseModel):
    delegated_agent: SpecializedAgent = Field(
        ...,
        description = "The name of the specialized agent to which the task has been delegated",
        examples = "Legal agent, Psychosocial Agent,Process Agent, Conversational agent"
    )
    content: Dict[str, Any] = Field(
        ...,
        description = "The response content from the delegated agent (Legal, Psychosocial, or Process), covering laws, emotional support, or administrative steps.",
        examples = r"'TAccording to Art. 42 of the ECA, the adopter must be at least 18 years old.' or [{'step': 1, 'status': 'Qualification'}, {'step': 2, 'status': 'Waiting List'}]'"
    )

