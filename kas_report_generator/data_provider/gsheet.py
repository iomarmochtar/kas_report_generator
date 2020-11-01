import datetime
from typing import List, Dict, Any
from google.oauth2.service_account import Credentials 
from googleapiclient import discovery
from .kas import Kas
from . import utils
from .monthly_kredit_debit import MonthlyKreditDebit, Record_T

DEFAULT_SCOPES: List[str] = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GSheet(object):
    def __init__(self, 
                 credentials: Dict[str, str], 
                 spreadsheet_id: str, 
                 scopes: List[str] = DEFAULT_SCOPES 
                 ):

        credentials: Credentials = Credentials.from_service_account_info(credentials, scopes=scopes)
        service: discovery.Resource = discovery.build('sheets', 'v4',credentials=credentials) 
        self.sheet: discovery.Resource = service.spreadsheets()
        self.spreadsheet_id: str = spreadsheet_id 

    def data_range(self, cell_range: str) -> list:
        data: Dict[str, Any] = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=cell_range
        ).execute()

        return data.get('values', [])

    def rekap_kas(self, begin_rekap: datetime.date, 
                        blacklist: List[str], 
                        untill: datetime.date = utils.now_date()) -> List[Dict]:
        return Kas(self, begin_rekap, untill, blacklist).summarize()

    def rekap_monthly_kredit_debit(self, month_index: int = utils.now().month) -> List[Record_T]:
        return MonthlyKreditDebit(self, month_index).summarize()
