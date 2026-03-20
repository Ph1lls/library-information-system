import mysql.connector


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="library_db",
        )

    def get_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]

    def get_table_data(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = cursor.column_names
        rows = cursor.fetchall()
        return columns, rows

    def call_procedure(self, name, params=()):
        cursor = self.conn.cursor()
        cursor.callproc(name, params)
        result_sets = []
        for result in cursor.stored_results():
            result_sets.append((result.column_names, result.fetchall()))
        return result_sets
