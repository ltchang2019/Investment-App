from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

print("Retrieving date range...")

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:
        adate -= timedelta(days=1)
    return adate

todayDate = "2019-06-20"
todayDate = datetime.strptime(todayDate, "%Y-%m-%d").date()
startDate = todayDate + relativedelta(months=-3)
prevWeekday = prev_weekday(todayDate)

print(startDate, "-", todayDate, "\n")
