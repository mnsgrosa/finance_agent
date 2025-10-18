from pydantic import BaseModel, Field
from typing import List, Dict

class Empresa(BaseModel):
    company_name: str = Field(..., description = "Company name")
    ticker: str = Field(..., description = "Ticker from company")

class EmpresasOutput(BaseModel):
    empresas: List[Empresa] = Field(..., description = "List of object Empresa")

class DataPoint(BaseModel):
    date: str = Field(..., description = "Point on the x axis")
    value: float = Field(..., description = "Point on the y axis")

class DataPoints(BaseModel):
    points: List[DataPoint] = Field(..., description = "List of objects datapoints")

class DbExists(BaseModel):
    tickers_stored: bool = Field(...,
                                description = "Boolean indicating if the tickers are stored in the database",
                                examples = r"{'tickers_stored': True}"
    )

class Ticker(BaseModel):
    ticker: str = Field(
        ...,
        description = "Ticker name"
        examples = r"{'ticker':'NATU3'}"
    )