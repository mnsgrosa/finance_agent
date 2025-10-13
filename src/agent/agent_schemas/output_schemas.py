from pydantic import BaseModel, Field
from typing import List, Dict

class EmpresasOutput(BaseModel):
    data: Dict[str, str] = Field(..., 
                                description = "Dictionary where each key is the name of the company and value the ticker symbol",
                                examples = r"{'natura':'nat4', 'petrobras':'petr4'}")

class DataPoints(BaseModel):
    points: Dict[str, float] = Field(...,
                                    description = "Dictionary where each key is a date in the format YYYY-MM-DD and value the closing price of the stock on that date",
                                    examples = r"{'2025-09-01': 23.45, '2025-09-02': 24.10}"
    )

class DbExists(BaseModel):
    tickers_stored: bool = Field(...,
                                description = "Boolean indicating if the tickers are stored in the database",
                                examples = r"{'tickers_stored': True}"
    )