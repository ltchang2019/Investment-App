from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from SP500DistributionDaysCopy import *
from NasdaqDistributionDaysCopy import *
import schedule
import time

print("Retrieving date range...")
global todayDate
todayDate = "2011-5-5"
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

def runAllDistribution():
    global todayDate
    print(todayDate)
    # if inUptrend == True:
    print("SP500:")
    getSP500Data(todayDate, prev_weekday(todayDate))
    checkForDistributionDaySP500(todayDate)
    checkOldestDaySP500(todayDate)
    checkDayCountSP500(todayDate)

    print("\nNasdaq:")
    getNasdaqData(todayDate, prev_weekday(todayDate))
    checkForDistributionDayNasdaq(todayDate)
    checkOldestDayNasdaq(todayDate)
    checkDayCountNasdaq(todayDate)
    print("\n \n")

    todayDate = next_weekday(todayDate)
    # elif inUptrend == False:
    #     print("In downtrend")


schedule.every(3).seconds.do(runAllDistribution)
while 1:
    schedule.run_pending()
    time.sleep(1)

startDate = todayDate + relativedelta(months=-3)
prevWeekday = prev_weekday(todayDate)

print(startDate, "-", todayDate, "\n")
