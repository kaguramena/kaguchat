# data/db_access.py
from db_config import get_db_connection

class DatabaseAccess:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection, self.cursor = self._get_cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

    def _get_cursor(self):
        connection = get_db_connection()
        if connection:
            return connection, connection.cursor(buffered=True)
        raise Exception("Database connection failed")

    def execute_query(self, query, params=None):
        with self:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        with self:
            self.cursor.execute(query, params or ())