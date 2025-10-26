import yfinance as yf
import investpy
import pandas as pd
from src.vectordb.databaase import FinancialDatabase
from typing import Dict, Any
from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.models.huggingface import HuggingFaceModel
# TODO: Import schemas
from dotenv import load_dotenv
import os

load_dotenv()

database = FinancialDatabase()

model = HuggingFaceModel(
    model_name = "cfahlgren1/natural-functions",
    api_key = os.getenv("HF_API_KEY"),
)

financial_agent = Agent(
    model,
    output_type = [EmpresasOutput, DbExists, DataPoints, Ticker],
    system_prompt = (
        r"""
        You are a financial expert agent, that whenever prompted to provide information about companies listed in the brazilian stock exchange (B3),
        whenever the user provides the name of a company, you should provide the ticker associated with it. If the tool that seaches the ticker was already
        used for this company before, you should check the previous messages sent for the ticker.

        The tools provided should be used whenever the user asks for information about a company listed in B3, and you should always use them

        TOOLS:
        1. Check_tickers: Tool that checks if the tickers were already stored in the database, should be the first one to be called,
        after that, if the tickers were not stored, call the store_tickers tool
        ARGS: None
        Returns: Returns a dictionary with a boolean whether the tickers were stored or not
        
        2. store_tickers: Tool responsible for the task of getting the name and ticker from each company listed at ibovespa
        it should be the first one called whenever the user asks for information about a company listed in B3
        ARGS: None
        Returns: Returns a dictionary where each company name is a key and the ticker is the value

        3. get_ticker: Tool that fetches the ticker from the company name provided from the API
        ARGS:
            company_name[str]: Company name that the user asked about
        Returns: Returns the ticker associated with the company name provided 

        4. get_ticker_plot: Tool that gets the ticker value daily and returns them from the dates given
        ARGS:
            company_name[str]: Company name that the user asked about
            start_date[str]: Date that user asked about should be formatted as "YYYY-MM-DD", defaults to '2025-09-01'
            end_date[str]: Date from end analisys should be formatted as "YYYY-MM-DD", defaults to '2025-10-01'
        Returns: Returns a dictionary where each key is a date in the format YYYY-MM-DD and value the closing price of the stock on that date
        
        Guidelines:
        - Before the first tool call, you should always call the check_tickers tool
        - If the tickers were not stored, you should call the store_tickers tool
        - If the user asks for information about a company and you haven't the company's ticker in your memory, you should call the get_ticker tool
        - If get_ticker tool doesnt return anything them, you should inform the user that the company was not found
        - If the user asks to plot about a company, check if you have the ticker in your memory than call the get_ticker_plot tool with its ticker
        - If the user asks for a plot of a company you should call the get_ticker_plot tool using the ticker stored in your memory
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
    return {"ticker": search_result.symbol}

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

    returnable_data = {date:value for date, value in zip(dates, values)}
    returnable_data_dict = DataPoints(points  = returnable_data)

    return returnable_data_dict