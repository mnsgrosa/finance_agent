from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from .supervised.legal_agent import legal_agent                # Antigo financial_agent from .supervised.finance_agent import financial_agent 
from .supervised.psychosocial_agent import psychosocial_agent  # Novo especialista (Apoio)
from .supervised.process_agent import process_agent            # Novo especialista (Burocracia)
from .supervised.conversational_agent import conversational_agent # Mantido para orquestração/conversa geral
from .supervisor_schema import SupervisorResponse
import logfire

logfire.configure(
    service_name = "agent_supervisor_service"
)
logfire.instrument_pydantic_ai()
#preciso ajustar A API KEY
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
    
    1. Legal Agent (Legal Expert): Specialist in the ECA ECA (Estatuto da Criança e do Adolescente) (Child and Adolescent Statute). Handles inquiries regarding qualification (habilitação), termination of parental rights, and legal deadlines.
    2. Psychosocial Agent (Support): Focuses on the child's profile, psychological preparation, "waiting time" vs. "desired profile," and the cohabitation stage.
    3. Process Agent (Bureaucracy): Consults status (simulated), required documents, and steps within the SNA (National Adoption System).
    4. Conversational Agent: Skilled in engaging in conversations about the brazilian adoption process.
    5. Explainable AI (XAI) Agent provides clear, human-understandable justifications for its reasoning and outputs.

    Guidelines:
    - Analyze the user's query carefully.
    - Determine which specialized agent is best suited to handle the query.
    - Delegate the task to the chosen agent and return the response to the user.
    - If the query involves multiple aspects, you may need to coordinate between agents.
    Always ensure that the user receives accurate and relevant information by leveraging the strengths of each specialized agent.
    """
)
@supervisor.tool
def delegate_to_legal_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about legal aspects of adoption,
    such as ECA (Child and Adolescent Statute), qualification process (habilitação), 
    termination of parental rights, legal deadlines, or any other legal procedures,
    this tool will delegate the task to the legal agent.
    """
    response = legal_agent.run_sync(query, usage=ctx.usage)
    ans = SupervisorResponse(
        delegated_agent="Legal Agent",
        content=response
    )
    return ans

@supervisor.tool
def delegate_to_psychosocial_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about psychological aspects of adoption,
    such as child profile selection, emotional preparation, waiting time vs desired profile,
    cohabitation stage, family adaptation, or any other psychosocial concerns,
    this tool will delegate the task to the psychosocial agent.
    """
    response = psychosocial_agent.run_sync(query, usage=ctx.usage)
    ans = SupervisorResponse(
        delegated_agent="Psychosocial Agent",
        content=response
    )
    return ans

@supervisor.tool
def delegate_to_process_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents questions about bureaucratic procedures,
    such as SNA (National Adoption System) status, required documentation, process steps,
    administrative deadlines, registration, or any other bureaucratic aspects,
    this tool will delegate the task to the process agent.
    """
    response = process_agent.run_sync(query, usage=ctx.usage)
    ans = SupervisorResponse(
        delegated_agent="Process Agent",
        content=response
    )
    return ans

@supervisor.tool
def delegate_to_conversational_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Based on the user query, if the user presents general conversations about adoption process,
    introductory questions, seeks general guidance, or needs engagement in broader discussions
    about Brazilian adoption without specific technical depth, this tool will delegate to the conversational agent.
    """
    response = conversational_agent.run_sync(query, usage=ctx.usage)
    ans = SupervisorResponse(
        delegated_agent="Conversational Agent",
        content=response
    )
    return ans

@supervisor.tool
def delegate_to_xai_agent(ctx: RunContext[None], query: str) -> SupervisorResponse:
    """
    Analyzes the user query and delegates to the conversational agent when appropriate.
    This XAI-enabled tool provides clear explanations for its delegation decisions.
    
    Criteria for delegation to conversational agent:
    1. General conversations about adoption process
    2. Introductory or orientation questions
    3. Requests for broad guidance or overview
    4. Emotional support or engagement needs
    5. Non-technical discussions about Brazilian adoption
    """
    response = conversational_agent.run_sync(query, usage=ctx.usage)
    ans = SupervisorResponse(
        delegated_agent="Explanable Agent",
        content=response
    )
    return ans