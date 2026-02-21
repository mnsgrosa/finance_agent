from pydantic import BaseModel, Field
from typing import List, Dict

class FinancialTickerOutput(BaseModel):
    ticker: str = Field(..., description = "Ticker symbol of the company", examples = "NAT3")

class DataPoint(BaseModel):
    point: Dict[str, float] = Field(..., description = "Dictionary with date as key and closing price as value")

class FinancialPlotOutput(BaseModel):
    points: List[DataPoints] = Field(..., description = "Data points for the financial plot")

class SummarizerNewsOutput(BaseModel):
    headline: str = Field(..., description="Headline of the news article")
    summary: str = Field(..., description="Summarized content of the news article")

class ConversationalOutput(BaseModel):
    content: str = Field(..., description="Response content from the conversational agent")



