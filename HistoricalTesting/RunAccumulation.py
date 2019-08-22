from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from SP500AccumulationDaysCopy import *
from NasdaqAccumulationDaysCopy import *
import schedule
import time

print("Retrieving date range...")
global todayDate
todayDate = "2019-06-21"
todayDate = datetime.strptime(todayDate, "%Y-%m-%d").date()

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:
        adate -= timedelta(days=1)
    return adate

def next_weekday(adate):
    adate += timedelta(days=1)
    while adate.weekday() > 4:
        adate += timedelta(days=1)
    return adate

def runAllAccumulation():
    global todayDate
    print(todayDate)
    # if inUptrend == True:
    print("SP500:")
    getSP500Data(todayDate, prev_weekday(todayDate))
    startSP500Function()
    print("\nNasdaq:")
    getNasdaqData(todayDate, prev_weekday(todayDate))
    startNasdaqFunction()
    print("\n \n")

    todayDate = next_weekday(todayDate)


schedule.every(3).seconds.do(runAllAccumulation)
while 1:
    schedule.run_pending()
    time.sleep(1)

startDate = todayDate + relativedelta(months=-3)
prevWeekday = prev_weekday(todayDate)

print(startDate, "-", todayDate, "\n")
