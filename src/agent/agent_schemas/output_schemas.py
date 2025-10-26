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
    company_name: str = Field(
        ...,
        description = "Company name",
        examples = r"{'company_name': 'Natura & Co Holding S.A.'}"
    )
    ticker: str = Field(
        ...,
        description = "Ticker name",
        examples = r"{'ticker':'NATU3'}"
    )

class CompanyData(BaseModel):
    company_name: str = Field(
        ...,
        description = "Company name",
        examples = r"{'company_name': 'Natura & Co Holding S.A.'}"
    )
    ticker: str = Field(
        ...,
        description = "Ticker from company",
        examples = r"{'ticker':'NATU3'}"
    )
    title: str = Field(
        ...,
        description = "News title about the company",
        examples = r"{'title': 'Natura & Co Holding S.A. Reports Strong Quarterly Earnings'}"
    )
    summarized_content: str = Field(
        ...,
        description = "News summarized about the company",
        examples = r"{'summarized_content': 'Natura & Co Holding S.A. reported a significant increase in quarterly earnings...'}"
    )