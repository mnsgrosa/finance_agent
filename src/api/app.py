from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, List
from src.api.db.data_storage import FinanceDb
from src.agent.agent_schemas.output_schemas import EmpresasOutput
import uvicorn

app = FastAPI()

db = FinanceDb()

class CompanyRequest(BaseModel):
    company_name: str = Field(...)

@app.get("/stored")
def checker():
    return {"exists": db.check()}

@app.post("/store_tickers")
def store_tickers(tickers: EmpresasOutput):
    data = [{"company_name":empresa.company_name, "ticker":empresa.ticker} for empresa in tickers.empresas]
    success = db.insert(data)
    return {"success": success}

@app.post("/get_ticker")
def get_ticker(company: CompanyRequest):
    company_name = company.company_name.lower()
    ticker = db.get_ticker(company_name)
    return {"ticker": ticker}

@app.get("/restart")
def restart_db():
    db.drop()
    db._check_schema()
    return {"message": "done"}

# TODO: API for insertion and querying of data from b3
if __name__ == '__main__':
    uvicorn.run(app)