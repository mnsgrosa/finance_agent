import chromadb
from uuid import uuid4

class FinancialDatabase:
    def __init__(self, persist_directory: str = "./financial_db"):
        self.client = chromadb.Client(chromadb.config.Settings(
            persist_directory=persist_directory
        ))
        self.collection = self.client.get_or_create_collection(name="financial_data")

    def add_company(self, company_name: str, ticker: str):
        record_id = str(uuid4())
        self.collection.add(
            ids = [record_id],
            documents = company_name,
            metadatas = {
                "ticker": ticker
            }
        )

    def get_company(self, company_name: str):
        result = self.collection.query(
            query_texts = [company_name],
            n_results = 1
        )
        return result.metadatas.get("ticker", None)

    def add_financial_news(self, summary: str, metadata: dict):
        record_id = str(uuid4())
        self.collection.add(
            ids = [record_id],
            document = [summary],
            metadatas = [metadata]
        )
    
    def get_financial_news(self, company_name: str, n_records: int = 5):
        results = self.collection.query(
            query_texts = [query],
            n_results = n_records,
            where = metadata
        )
        return results