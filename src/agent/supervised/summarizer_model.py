from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool, DuckDuckGoResult
from dotenv import load_dotenv
from ..agent_schemas.output_schemas import SummarizerNewsOutput
from src.vectordb.database import FinancialDatabase
from transformers import pipeline
from datetime import datetime
import os

load_dotenv()
database = FinancialDatabase()

summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
news_summarizer_model = HuggingFaceModel("cfahlgren1/natural-functions", api_key = os.getenv("HF_API_KEY"))

summarizer_agent = Agent(
    summarizer_model, 
    tools = [duckduckgo_search_tool()],
    output_type = [SummarizerNewsOutput],
    system_prompt = r"""
    You are an agent that will use the duckduckgo_search_tool using its output for other defined tools such as summarize_news.
    """
)

@summarizer_agent.tool()
def summarize_news(context: RunContext, company_name: str, news: DuckDuckGoResult) -> dict[str, str]:
    """
    Tool that should receive the output from duckduck_go_search_tool and summarize it
    ARGS:
        company_name[str]: Name of the company prompted by the user
        news[DuckDuckGoResult]: Name of the company to search news for
    Returns: Returns a dictionary with the headline and summarized content of the news article
    """
    body = news.body
    ticker = database.get_company(company_name)
    summarized_content = summarization_pipeline(body, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    metadata = {
        "ticker": ticker,
        "date": datetime.now().isoformat()
    }
    
    database.add_financial_news(
        summary = summarized_content,
        metadata = metadata
    )

    return {
        "headline": news.title,
        "summary": summarized_content
    }