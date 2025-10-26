from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from dotenv import load_dotenv
from src.agent.agent_schemas.output_schemas import CompanyData
from transformers import pipeline
import os

load_dotenv()

summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
news_summarizer_model = HuggingFaceModel("cfahlgren1/natural-functions", api_key = os.getenv("HF_API_KEY"))

summarizer_agent = Agent(
    summarizer_model, 
    output_type = CompanyData
)
