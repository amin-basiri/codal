import pyodbc
import os


class SQLBackend:
    def __init__(self, database, username, password, driver='{ODBC Driver 17 for SQL Server}', server='.'):
        self.connection = pyodbc.connect(
            'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'.format(
                driver=driver,
                server=server,
                database=database,
                username=username,
                password=password,
            )
        )

        self.cursor = self.connection.cursor()

    def commit(self, query):
        self.cursor.execute(query)
        self.cursor.commit()

    def databases(self):
        self.cursor.execute('SELECT * FROM sys.databases')
        return self.cursor.fetchall()


sql = SQLBackend(
    database=os.environ.get('SQL_DATABASE'),
    username='sa',
    password=os.environ.get('SA_PASSWORD'),
    server=os.environ.get('SQL_SERVER'),
)

print(sql.databases())