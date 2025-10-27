from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from .supervised.finance_agent import financial_agent
from .supervised.summarizer_model import summarizer_agent
from .supervised.conversational_agent import conversational_agent
from .supervisor_schema import SupervisorResponse
import logfire

logfire.configure(
    service_name = "agent_supervisor_service"
)
logfire.instrument_pydantic_ai()

supervisor_model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

supervisor = Agent(
    supervisor_model,
    output_type = [SupervisorResponse],
    system_prompt = r"""
    You are an agent supervisor, your role is to delegate tasks to specialized agents based on user queries.
    Interpret which agent is best suited to handle the request and forward the task accordingly.
    After interpreting you can rewrite the query to better fit the specialized agent context.
    You have access to the following agents:

    1. Financial Agent: Agent with tools destined to get ticker information and get data points from brazilian stock market.
    2. Summarizer Agent: Specializes in gathering information with duckduckgo tool and call an summarizer to store news in the vectordb.
    3. Conversational Agent: Skilled in engaging in conversations about the brazilian stock market.

    Guidelines:
    - Analyze the user's query carefully.
    - Determine which specialized agent is best suited to handle the query.
    - Delegate the task to the chosen agent and return the response to the user.
    - If the query involves multiple aspects, you may need to coordinate between agents.

    Always ensure that the user receives accurate and relevant information by leveraging the strengths of each specialized agent.
    """
)

@supervisor.tool
def delegate_to_financial_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about financial data, as company ticker, stock prices
    ,store ticker or plot ticker data, this tool will delegate the task to the financial agent.

    If necessary 
    """
    response = financial_agent.run_sync(query, usage = ctx.usage)
    ans = SupervisorResponse(
        delegated_agent = "Financial Agent",
        content = response
    )
    return ans

@supervisor.tool
def delegate_to_summarizer_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about news summarization, headlines extraction
    ,this tool will delegate the task to the summarizer agent.

    This agent will summarize data and store on the vector database.
    """
    response = summarizer_agent.run_sync(query, usage = ctx.usage)
    ans = SupervisorResponse(
        delegated_agent =  "Summarizer Agent",
        content = response
    )
    return ans

@supervisor.tool
def delegate_to_conversational_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about conversational data regarding the brazilian stock market,
    this tool will delegate the task to the conversational agent.

    this agent will get data summarized by the summarized stored on the vector database and answer user questions regarding the data.
    """
    response = conversational_agent.run_sync(query, usage = ctx.usage)
    ans = SupervisorResponse(
        delegated_agent = "Conversational Agent",
        content = response
    )
    return ans