from fastapi import FastAPI
from .db.data_storage import DataStorage
app = FastAPI()

db = DataStorage()

@app.get("/stored")
def checker():
    return {"exists": db.check()}

@app.post("/store_tickers")
def store_tickers(tickers: Dict[str, str]):
    data = [{"company_name": name.lower(), "ticker": ticker} for name, ticker in tickers.items()]
    success = db.insert(data)
    return {"success": success}

@app.post("/get_ticker")
def get_ticker(company_name: str):
    company_name = company_name.lower()
    ticker = db.get_ticker(company_name)
    return {"ticker": ticker}

# TODO: API for insertion and querying of data from b3
