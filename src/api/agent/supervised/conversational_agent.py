from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from dotenv import load_dotenv
from .vectordb.database import FinancialDatabase
from ..agent_schemas.output_schemas import ConversationalOutput
from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

conversational_pipeline = pipeline("text2text-generation")

database = FinancialDatabase()

rag_model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

rag_agent = Agent(
    rag_model,
    output_schemas = [ConversationalOutput],
    system_prompt = r"""
    You are an agent that will use the vectordb to provide context for an agent stored in your tool.
    Your input will be given by a supervisor agent that will delegate tasks to you when the user has questions about the brazilian stock market.
    """
)

@rag_agent.tool
def get_context_from_vectordb(ctx: RunContext[None], company_name: str, n_records: int, prompt: str) -> str:
    """
    Tool that fetches context from the vectordb based on the supervisor rewritten query.
    ARGS:
        context[RunContext]: Context of the agent run
        company_name[str]: Company name that the user asked about
        n_records[int]: Number of records to fetch from the vectordb
        prompt[str]: The rewritten prompt from the supervisor agent for the conversational agent answering the user
    Returns:
        Returns string from a llm with the context fetched from the vectordb
    """
    context = database.get_financial_news(company_name, n_records)
    context = " ".join([item['document'] for item in context['documents']])
    combined_context = f"{prompt} context: ".join(context)
    ans = conversational_pipeline(combined_context, max_length=200, num_return_sequences=1)[0]['generated_text']
    return ConversationalOutput(content = ans)