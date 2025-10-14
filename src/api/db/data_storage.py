import sqlite3
import pandas as pd
from typing import Dict, List, Any
from contextlib import contextmanager
# from src.utils.logger import setup_logging

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
            cursor = self.conn.cursor()
            yield cursor
            self.conn.commit()
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise e  
        finally:
            if cursor:
                cursor.close()  

    def _check_schema(self):
        with self.get_cursor() as cursor:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS b3 (
                        company_name TEXT,
                        ticker TEXT,
                    UNIQUE (company_name, ticker)
                    );
            '''
            )
        return None
    
    def insert(self, data:List[Dict[str, Any]]):
        if data is None:
            return False
        
        insertion_query = """
            INSERT INTO b3 (company_name, ticker)
            VALUES (?, ?)
            ON CONFLICT DO NOTHING
            """
        
        try:
            data_to_insert = [
                (d['company_name'], d['ticker']) for d in data
            ]

            with self.get_cursor() as cursor:
                cursor.executemany(insertion_query, data_to_insert)
            return "Succes"
        except Exception as e:
            return f"Error: {e}"
        
    def get_ticker(self, company_name: str):
        query = f'''
            SELECT ticker FROM b3
            WHERE company_name = '{company_name}'
        '''

        df = pd.read_sql_query(query, self.conn)
        values = df.to_dict('records')
        return values

    def check(self):
        query = f'''
            SELECT COUNT(*) as count FROM b3
        '''

        with self.get_cursor() as cursor:
            value = cursor.execute(query).fetchone()[0]
        
        return False if value < 1 else True

    def drop(self):
        query = f"""
            DROP TABLE b3
        """

        with self.get_cursor() as cursor:
            cursor.execute(query)
        
        return None