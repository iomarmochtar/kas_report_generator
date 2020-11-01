import re
from datetime import datetime, date
from typing import Union, Pattern, Dict, Any, List
from .exceptions import DataValidationFailed
from . import utils

# regex parser for date pattern 10-Oct-20
DATE_RE: Pattern = re.compile(r'\d+-(?P<month>\w+)-\d{2}')
# regex parser for cleanup money pattern
MONEY_re: Pattern = re.compile(r'(Rp|,)')

COL_MAPPER: list = ['tgl', 'ket', 'kredit', 'debit', 'saldo']
POINT_ROW: int = 4
DATE_FORMAT: str = '%d-%b-%y'

Record_T = Dict[str, Union[str, int, date]]

def convert_money(val: str) -> int:
    """
    Convert money string pattern to number
    """
    if not val:
        return 0

    clean_up = MONEY_re.sub('', val)
    if not clean_up.isdigit():
        raise DataValidationFailed(f'Wrong money pattern: {val}')
    
    return int(clean_up)

class MonthlyKreditDebit(object):
    
    def __init__(self, gsheet, 
                month_index: int,
                record_per_page: int = 5
                ):
        self.gsheet = gsheet
        self.record_per_page: int = record_per_page 
        self.month_index: int = month_index
        self.__total: Dict[str,int] = {}

    def incr_total(self, key, amount):
        if key not in self.__total:
            self.__total[key] = 0
        self.__total[key] += amount

    def parse_value(self, row: List[str]) -> Record_T:
        
        if len(COL_MAPPER) != len(row):
            raise DataValidationFailed(
                    f'data not length not match => {len(row)} ({row})'
                )

        result: Record_T = dict(zip(COL_MAPPER, row))

        result.update({
            'tgl': datetime.strptime(result['tgl'], DATE_FORMAT).date(),
            'kredit': convert_money(result['kredit']),
            'debit': convert_money(result['debit']),
            'saldo': convert_money(result['saldo'])
        })

        if result['kredit'] == 0 and result['debit'] == 0:
            raise DataValidationFailed(f'Invalid data, both kredit and debit has zero value')

        return result

    def do_scroll(self,  page: int=1) -> List[Record_T]:
        min_pr: int = POINT_ROW - 1
        range_top: int = page * self.record_per_page
        range_bottom: int = range_top - (self.record_per_page - 1)
        # Starting in cell B4
        point1, point2 = [ min_pr + x for x in [range_bottom, range_top] ]
        cell1: str = f'B{point1}'
        cell2: str = f'F{point2}'
        cell_range: str = f'Pembukuan!{cell1}:{cell2}'
        cell_data: list = self.gsheet.data_range(cell_range)
        result: list = []

        for row in cell_data:
            parsed: Dict[str, Union[str,int]] = self.parse_value(row)

            # if the month sequence was not same means time to stop
            if parsed['tgl'].month != self.month_index:
                break
            result.append(parsed)

            self.incr_total('kredit', parsed['kredit'])
            self.incr_total('debit', parsed['debit'])
        return result

    def summarize(self) -> Dict[str, Any]:
        page: int = 1
        detail: List[Record_T] = []

        # keep scrolling untill the data list based on date not matched
        while True:
            records: List[Record_T] = self.do_scroll(page=page)
            page += 1
            if not records:
                break

            detail.extend(records)

        # reverse it since the latest record in most top
        detail.reverse()
        return {
            'total': self.__total,
            'detail': detail
        }