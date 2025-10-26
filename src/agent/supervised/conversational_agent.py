from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel

conv_model = HuggingFaceModel(
    model_name = "mistralai/Mistral-7B-v0.1",
    api_key = os.getenv("HF_API_KEY")
)

conversational_agent = Agent(
    conv_model,
    system_prompt = r"""
    You are a brazilian stock market expert agent, based on given news you will
    answer about the user questions regarding the provided stock
    """
)