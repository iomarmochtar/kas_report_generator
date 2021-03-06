import pickle
import datetime
from . import utils
from collections import OrderedDict
from typing import List, Dict, Any

CELL_RANGE: str = 'Rekap Detail Iuran!B5:37'

class Rumah(object):
    def __init__(self, no: str, nama: str, 
                 rekaps: Dict[datetime.date, str]):
        self.no = no
        self.nama = nama
        self.rekaps = rekaps

class Kas(object):
    rumahs: Dict[str, Rumah] = OrderedDict()

    def __init__(self,
                 gsheet,
                 begin_rekap: datetime.date,
                 untill: datetime.date,
                 blacklist: List[str] = []
                 ):
        self.untill = untill
        self.gsheet = gsheet
        self.blacklist: List[str] = blacklist
        self.begin_rekap: datetime.date = begin_rekap
        self.parse()

    @property
    def sheet_data(self) -> dict:
        return self.gsheet.data_range(CELL_RANGE)

    def parse(self):
        for value in self.sheet_data:
            no, nama = value[0:2]
            rekaps: list = value[2:]
            rumah = Rumah(no=no, nama=nama, 
                          rekaps=self.normalize_rekap(rekaps))
            self.rumahs[no] = rumah 

    def normalize_rekap(self, rekaps: List[str]) -> Dict[datetime.date, str]:
        """
        Normalisasi data rekap dengan tanggalnya
        """

        result: Dict[datetime.date, str] = OrderedDict()
        if not rekaps:
            return result

        year_counter: int = self.begin_rekap.year
        month_counter: int = self.begin_rekap.month

        for rekap in rekaps:
            date = utils.gen_date(month=month_counter, year=year_counter)
            result[date] = rekap

            month_counter += 1 
            # reset
            if month_counter == 13:
                month_counter = 1
                year_counter += 1

        return result
    
    def summarize(self) -> List[Dict[str, Any]]:
        result: List[Dict] = []

        for no, rumah in self.rumahs.items():
            score = None
            rekap_months = list(rumah.rekaps.keys())
            if rekap_months:
                last_iuran = rekap_months[-1]
                score = -(utils.diff_month(last_iuran, self.untill))

            result.append({
                'no': no,
                'nama': rumah.nama,
                'score': score,
                'is_blacklisted': no in self.blacklist,
                'rekaps': rekap_months 
            })
        return result