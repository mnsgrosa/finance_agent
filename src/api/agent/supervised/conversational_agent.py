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

database = FaqDatabase() #mudei

#database = FinancialDatabase() 

rag_model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

rag_agent = Agent(
    rag_model,
    output_schemas = [ConversationalOutput],
    system_prompt = r"""
    You are a Retrieval‑Augmented Generation conversational agent specialized in the Brazilian child and adolescent adoption process.
    A supervisor agent will send you the user’s question.
    Your tasks:
        - Understand the question.
        - Query the vector database using semantic search.
        - Use only the retrieved context plus general reasoning to answer clearly and empathetically in Brazilian Portuguese.
    Scope:
        - basic concepts of adoption, main legal framework at a high level, typical process steps (qualification, registration in the national system, matching, cohabitation, court decision), and non‑clinical psychosocial guidance (expectations, child profile, waiting time, family preparation).
    Limits:
        - you do not provide legal advice, psychological treatment or clinical diagnosis; you must not invent case data, deadlines or confidential information. If the context does not contain enough information, say so and suggest that the person contact official services (juvenile court, public defender’s office, prosecutor’s office, social services or mental‑health professionals).
    """
)

#adaptar esse Código abaixo
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