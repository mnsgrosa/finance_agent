import os
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ToolReturn, BinaryContent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAiChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from src.agent.agent_schemas.output_schemas import ...
from src.agent.agent_schemas.dataclasses import ... 

ollama_model = OpenAiChatModel(
    model_name = ...,
    provider = OllamaProvider(base_url = 'http://localhost:11434/v1')
)


agent = Agent(
    ollama_model,
    output_type = [..., str],
    system_prompt = (
        ...
    )
)