import datetime
from typing import List, Dict
from google.oauth2.service_account import Credentials 
from googleapiclient import discovery
from .kas import Kas

DEFAULT_SCOPES: List[str] = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class GSheet(object):
    def __init__(self, 
                 credentials: Dict[str, str], 
                 spreadsheet_id: str, 
                 cell_range: str,
                 scopes: List[str] = DEFAULT_SCOPES 
                 ):

        credentials: Credentials = Credentials.from_service_account_info(credentials, scopes=scopes)
        service = discovery.build('sheets', 'v4',credentials=credentials) 
        self.sheet = service.spreadsheets()
        self.spreadsheet_id: str = spreadsheet_id 
        self.cell_range: str = cell_range

    @property 
    def cell_data(self) -> dict:
        return self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.cell_range
        ).execute()

    def rekap_kas(self, begin_rekap: datetime.date, blacklist: List[str]) -> List[Dict]:
        return Kas(self.cell_data, begin_rekap, blacklist).summarize()
