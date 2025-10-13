import sqlite3
import pandas as pd
from typing import Dict, List, Any
from contextlib import contextmanager
from src.utils.logger import MainLogger

class FinanceDb:
    def __init__(self):
        self.schema_name = "b3"
        self.conn = sqlite3.connect("finance.db", check_same_thread = False)
        self._check_schema()
        self.db_file = "finance.db"

    @contextmanager
    def get_cursor(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file, check_same_thread = False)
        
        cursor = None
        try:
            self.info("Creating cursor")
            cursor = self.conn.cursor()
            yield cursor
            self.info("Committing changes")
            self.conn.commit()
        except Exception as e:
            self.error(f"Error during transaction: {e}. Rolling back changes.")
            if self.conn:
                self.conn.rollback()
            raise e  
        finally:
            if cursor:
                self.info("Closing cursor")
                cursor.close()  

    def _check_schema(self):
        self.info("Checking the schema")
        with self.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS b3 (
                    company_name TEXT,
                    ticker TEXT
                );
            ''')
        return
    
    def insert(self, data:List[Dict[str, Any]]):
        if data is None:
            self.error("Empty data")
            return False
        
        insertion_query = """
            INSERT INTO b3 (company_name, ticker)
            VALUES (?, ?)
            ON CONFLICT DO NOTHING
            """
        
        try:
            self.info("Starting insertion")
            data_to_insert = [
                (
                    d['company_name'], 
                    d['ticker'], 
                ) for d in data
            ]

            with self.get_cursor() as cursor:
                cursor.executemany(insertion_query, data_to_insert)
            self.info("Insertion done")
            return True
        except Exception as e:
            self.error(f"Error while inserting data to the db: {e}")
            return False
        
    def get_ticker(self, company_name: str):
        query = f'''
            SELECT ticker FROM b3
            WHERE company_name = '{company_name}'
        '''

        df = pd.read_sql_query(query, self.conn)
        return df

    def check(self):
        query = f'''
            SELECT COUNT(*) as count FROM b3
        '''

        df = pd.read_sql_query(query, self.conn)
        return True if df.shape[0] > 0 else False