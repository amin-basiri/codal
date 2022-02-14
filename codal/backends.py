import pyodbc
import os
from bs4 import BeautifulSoup

from codal.models import Report
from codal.exceptions import ReportExtractorException
from codal import utils


class BaseStoreBackend:
    def insert(self, **kwargs):
        raise NotImplementedError


class SQLStoreBackend(BaseStoreBackend):
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

    def insert(self, table, values):
        self.commit("INSERT INTO {table} VALUES ({values});".format(
            table=table,
            values=values,
        ))


class ReportExtractorBackend:

    def __init__(self, store: BaseStoreBackend):
        self._store = store

        self.ReportDefaults = {
            "صورت وضعیت مالی": {
                "extraction_method": self._extract_financial_statements_report,
                "table_name": "codal_tbl",  # TODO must change and generalize
                "max_column": 11,
            },
        }

    def extract(self, report: Report):
        defaults = self.ReportDefaults.get(report.type)
        if not defaults:
            raise ReportExtractorException("Report type undefined.")

        defaults['extraction_method'](report)

    def _extract_financial_statements_report(self, report):
        with open(report.path, 'rt', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

            period_end_date = soup.select('#ctl00_lblPeriodEndToDate')[0].text
            report_name = soup.select('#ddlTable option[selected]')[0].text
            report_name = utils.convert_report_type_name(report_name)
            is_audited = soup.select('#ctl00_lblIsAudited')[0].text
            # symbol = soup.select('#ctl00_txbSymbol')[0].text  # Some Symbol Names Are Incorrect
            symbol = report.letter.symbol

            fixed_columns = [period_end_date, report_name, is_audited, symbol]

            max_header_size = 0

            for tr in soup.select('table thead tr'):
                ths = [th.text for th in tr.select('th')] if len(tr.select('th')) >= max_header_size else [''] + [
                    th.text for th in tr.select('th')] + ['', '']

                row = ','.join([f"N'{th}'" for th in ths[:len(ths) - 1]])
                row += ','
                row += ','.join([f"N'{data}'" for data in fixed_columns])
                row += ','
                row += ','.join([f"N''" for i in range(1, self.ReportDefaults[report.type]['max_column'] - len(ths) - len(fixed_columns) + 2)])

                max_header_size = len(ths) if len(ths) > max_header_size else max_header_size

                self._store.insert(
                    table=self.ReportDefaults[report.type]['table_name'],
                    values=row
                )

            for tr in soup.select('table tbody tr')[2:]:
                tds = [td.text for td in tr.select('td')]

                row = ','.join([f"N'{td}'" for td in tds[:len(tds) - 1]])
                row += ','
                row += ','.join([f"N'{data}'" for data in fixed_columns])
                row += ','
                row += ','.join([f"N''" for i in range(1, self.ReportDefaults[report.type]['max_column'] - len(tds) - len(fixed_columns) + 2)])

                self._store.insert(
                    table=self.ReportDefaults[report.type]['table_name'],
                    values=row
                )


sql = SQLStoreBackend(
    database=os.environ.get('SQL_DATABASE'),
    username='sa',
    password=os.environ.get('SA_PASSWORD'),
    server=os.environ.get('SQL_SERVER'),
)

extractor = ReportExtractorBackend(sql)
