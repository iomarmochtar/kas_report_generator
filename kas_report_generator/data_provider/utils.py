import datetime
from typing import List

def gen_date(month: int, year: int) -> datetime.date:
    return datetime.date(year, month, 1)

def diff_month(begin: datetime.date, end: datetime.date) -> int:
    return (end.year - begin.year) * 12 + (end.month - begin.month)

def previous_month(date: datetime.date) -> datetime.date:
    """
    Get previous date of month (first one) from given date
    """
    return (date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)

def range_prev_months(begin_date: datetime.date, num: int) -> List[datetime.date]:
    result: List[datetime.date] = [begin_date]
    for _ in range(num):
        result.insert(0, previous_month(result[0]))
    return result

def now() -> datetime.datetime:
    return datetime.datetime.now()

def now_date(dt: datetime.datetime = now()) -> datetime.date:
    return dt.date()