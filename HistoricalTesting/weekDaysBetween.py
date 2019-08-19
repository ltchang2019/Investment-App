import datetime
from GetDateRangeCopy import todayDate
from dateutil.relativedelta import relativedelta

def weekDaysBetween(firstDate, lastDate):
    start = firstDate
    end = lastDate

    daydiff = end.weekday() - start.weekday()

    days = ((end-start).days - daydiff) / 7 * 5 + min(daydiff,5) - (max(end.weekday() - 4, 0) % 5)

    return days
