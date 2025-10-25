import pyodbc

SERVER = 'ZANLAPT\SQLEXPRESS'
DATABASE = 'InfinityTech'

def get_connection():
    try:
        connection_string = (f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                             f"SERVER={SERVER};"
                             f"DATABASE={DATABASE};"
                             f"Trusted_Connection=yes;"
                             f"TrustServerCertificate=yes;")
        return pyodbc.connect(connection_string)
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None