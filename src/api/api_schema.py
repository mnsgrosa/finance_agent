from pydantic import BaseModel, Field
from typing import Dict, Any

class ApiResponseSchema(BaseModel):
    delegated_agent: str = Field(..., description="Name of agent responsible", examples="Financial, Summarizer, Conversational")
    content: Dict[str, Any] = Field(..., description="Data returned by the API")