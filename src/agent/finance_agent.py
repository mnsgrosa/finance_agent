import os
import yfinance as yf
import pandas as pd
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ToolReturn, BinaryContent
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from src.agent.agent_schemas.output_schemas import (
    EmpresasOutput, 
    DataPoints,
    DbExists
)
from src.utils.logger import setup_logging

setup_logging(service_name = "Financial-agent")

ollama_model = OpenAIChatModel(
    model_name = "qwen2.5:14b",
    provider = OllamaProvider(base_url = "http://localhost:11434/v1")
)

agent = Agent(
    ollama_model,
    output_type = [EmpresasOutput, DbExists, DataPoints, str],
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

@agent.tool
def check_tickers(context: RunContext[Dict]) -> Dict[str, bool]:
    """
    Tool that checks if the tickers were already stored in the database, should be the first
    tool called, after that, if the tickers were not stored, call the store_tickers tool
    ARGS:
        context[RunContext]: Context of the agent run
    Returns:
        Returns a dictionary with the tickers if they were found, or an empty dictionary if not
    """
    with httpx.Client() as client:
        response = client.get("http://localhost:8000/stored")
        if response.status_code == 200:
            data = response.json()
            if data.get("exists", False):
                return {"tickers_stored": True}
    return {"tickers_stored": False}

@agent.tool
def store_tickers(context: RunContext[Dict]) -> Dict[str, str]:
    """
    Tool responsible for the task of getting the name and ticker from each company listed at ibovespa
    it will create a dictionary where each company name is the key and the ticker the value
    this tool should be called if you haven't called it before
    ARGS:
        context[RunContext]: Context of the agent run
    Returns:
        Returns a dictionary with a message if wether the operation was successful or not
    """
    with httpx.Client() as client:
        response = client.get("https://www.infomoney.com.br/cotacoes/empresas-b3/")
        response.raise_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    empresas = soup.find_all("td", class_ = "higher")
    empresas = [empresa.text.lower() for empresa in empresas]

    tickers = soup.find_all("td", class_ = "strong")
    tickers = [ticker.text for ticker in tickers]

    tickers_dict = {empresa:ticker for empresa, ticker in zip(empresas, tickers)}

    with httpx.Client() as client:
        response = client.post("http://localhost:8000/store_tickers", json = tickers_dict)
        if response.status_code != 200:
            raise Exception("Error storing tickers via API")

    return {"message": response.text}

@agent.tool
def get_ticker(context: RunContext[Dict], company_name: str) -> Dict[str, str]:
    """
    Tool that fetches the ticker from the company name provided from the API
    ARGS:
        context[RunContext]: Context of the agent run
        company_name[str]: Company name that the user asked about
    Returns:
        Returns the ticker associated with the company name provided
    """
    with httpx.Client() as client:
        response = client.post("http://localhost:8000/get_ticker", json={"company_name": company_name})
        if response.status_code == 200:
            data = response.json()
            return {"ticker": data.get("ticker", None)}
    return {"ticker": None}

@agent.tool
def get_ticker_plot(context: RunContext[Dict], company_ticker: str, start_date: str = "2025-09-01", end_date: str = "2025-10-01") -> Dict[str, float]:
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
    data = yf.download(company_ticker + ".SA", start = start_date, end = end_date, progress = False)
    dates = data.index.strftime("%Y-%m-%d").tolist()
    values = data['Close'].round(2).tolist()

    returnable_data = {date:value for date, value in zip(dates, values)}
    returnable_data = DataPoints(points  = returnable_data)

    return returnable_data

class FinanceAgent:
    def __init__(self, agent):
        self.agent = agent
        self.response = None

    def run(self, prompt: str) -> ToolReturn:
        if self.response is None:
            response = self.agent.run_sync(prompt)
        else:
            response = self.agent.run_sync(prompt, message_history = self.response)
        self.response = response
        return response

if __name__ == "__main__":
    agent = FinanceAgent(agent)
    print(agent.run("Hi, can you provide me the ticker for natura?"))