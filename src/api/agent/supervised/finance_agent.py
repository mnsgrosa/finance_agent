
### EXCLUIR

import yfinance as yf
import investpy
import pandas as pd
from src.vectordb.database import FinancialDatabase
from typing import Dict, Any
from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
from dotenv import load_dotenv
from ..agent_schemas.output_schemas import FinancialTickerOutput, FinancialPlotOutput
import os

load_dotenv()

database = FinancialDatabase()

model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

financial_agent = Agent(
    model,
    output_type = [FinancialTickerOutput, FinancialPlotOutput],
    system_prompt = (
        r"""
        You are an brazillian stock market agent specialized in gathering financial stock market data.
        whenever prompted to get specified ticker you will use the get_ticker tool. This tool will not only return the ticker but also store it at the database for future usage.
        Whenever prompted to get ticker plot data you will use the get_ticker_plot tool. This tool will return a list of datapoints where each datapoint is a dictionary with date as key and closing price as value.

        Prompts given for you are rewritten by a supervisor agent, so they will be intended to guide you to use your tools properly.

        Guidelines:
        - Always use the tools provided to you to gather information.
        - Ensure to only provide data given by your tools.
        """
    ),
    deps_type = dict
)

@financial_agent.tool
def get_ticker(context: RunContext[Dict], company_name: str) -> Dict[str, str]:
    """
    Tool that fetches the ticker from the company name provided from investpy API and stores at the database
    ARGS:
        context[RunContext]: Context of the agent run
        company_name[str]: Company name that the user asked about
    Returns:
        Returns the ticker associated with the company name provided
    """
    search_result = investpy.search_quotes(
        text = company_name,
        products = ["stocks"],
        countries = ["brazil"],
        n_results = 1
    )
    database.add_company(company_name, search_result.symbol)
    return FinancialTickerOutput(ticker = search_result.symbol)

@financial_agent.tool
def get_ticker_plot(context: RunContext[Dict], company_name: str, start_date: str = "2025-09-01", end_date: str = "2025-10-01") -> DataPoints:
    """
    Tool that gets the ticker value daily and returns them from the dates given
    ARGS:
        context[RunContext]: Context of the agent run
        company_name[str]: Company name that the user asked about
        start_date[str]: Date that user asked about should be formatted as "YYYY-MM-DD", defaults to '2025-09-01'
        end_date[str]: Date from end analisys should be formatted as "YYYY-MM-DD", defaults to '2025-10-01'
    Returns:
        Returns a dictionary where each key is a date in the format YYYY-MM-DD and value the closing price of the stock on that date
    """
    result = database.get_company(company_name)

    if not result:
        result = get_ticker(context, company_name).get("ticker")

    data = yf.download(result + ".SA", start = start_date, end = end_date, progress = False)
    dates = data.index.strftime("%Y-%m-%d").tolist()
    values = data['Close'].round(2).tolist()

    returnable_data = [{date:value} for date, value in zip(dates, values)]
    returnable_data_validated = FinancialPlotOutput(points = returnable_data)

    return returnable_data_validated