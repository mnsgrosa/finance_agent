from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic import BaseModel
from src.agent.supervised.finance_agent import financial_agent
from src.agent.supervised.summarizer_model import summarizer_agent
from src.agent.supervised.conversational_agent import conversational_agent

supervisor_model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

agent_supervisor = Agent(
    supervisor_model,
    system_prompt = r"""
    You are an agent supervisor, your role is to delegate tasks to specialized agents based on user queries.
    You have access to the following agents:

    1. Financial Agent: Expert in financial data and stock market information.
    2. Summarizer Agent: Specializes in summarizing news articles and extracting key information.
    3. Conversational Agent: Skilled in engaging in conversations about the brazilian stock market.

    Guidelines:
    - Analyze the user's query carefully.
    - Determine which specialized agent is best suited to handle the query.
    - Delegate the task to the chosen agent and return the response to the user.
    - If the query involves multiple aspects, you may need to coordinate between agents.

    Always ensure that the user receives accurate and relevant information by leveraging the strengths of each specialized agent.
    """
)

@agent_supervisor.tool
def delegate_to_financial_agent(ctx: RunContext[None], query: str) -> ToolReturn:
    """
    Based on the user query, if the user presents questions about financial data, as company ticker, stock prices
    ,store ticker or plot ticker data, this tool will delegate the task to the financial agent.
    """
    response = financial_agent.run_sync(query, usage = ctx.usage)
    return ToolReturn(content=response)


@agent_supervisor.tool
def delegate_to_summarizer_agent(ctx: RunContext[None], query: str) -> ToolReturn:
    """
    Based on the user query, if the user presents questions about news summarization, headlines extraction
    ,this tool will delegate the task to the summarizer agent.

    This agent will summarize data and store on the vector database.
    """
    response = summarizer_agent.run_sync(query, usage = ctx.usage)
    return ToolReturn(content=response)

@agent_supervisor.tool
def delegate_to_conversational_agent(ctx: RunContext[None], query: str) -> ToolReturn:
    """
    Based on the user query, if the user presents questions about conversational data regarding the brazilian stock market,
    this tool will delegate the task to the conversational agent.

    this agent will get data summarized by the summarized stored on the vector database and answer user questions regarding the data.
    """
    response = conversational_agent.run_sync(query, usage = ctx.usage)
    return ToolReturn(content=response)