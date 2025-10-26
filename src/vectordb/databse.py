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

    def add_chunks(self, chunks: dict):
        for chunk in chunks:
            record_id = str(uuid4())
            documents = chunk['documents']
            metadata = chunk['metadata']
            self.collection.add(
                ids = [record_id],
                documents =[documents],
                metadatas = [metadata]
            )

    def add_financial_record(self, document: str, metadata: dict):
        self.collection.add(
            ids = [record_id],
            embeddings= [document],
            metadatas = [metadata]
        )
    
    def get_record(self, query: str, metadata: dict, n_records: int = 1):
        results = self.collection.query(
            query_texts = [query],
            n_results = 1,
            where = metadata
        )
        return results