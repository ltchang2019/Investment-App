from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from SP500PostFollowThrough import *
from NasdaqPostFollowThrough import *
import mysql.connector
import schedule
import time

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)

print("Retrieving date range...")
global todayDate
todayDate = "2015-10-06"
todayDate = datetime.strptime(todayDate, "%Y-%m-%d").date()

def StartSP500PostFollowThrough():
    sql = "SELECT upOrDown FROM SP500PostFollowThrough"
    mycursor.execute(sql)
    if mycursor.rowcount < 3:
        runAllPostFollowThrough()
    elif mycursor.rowcount == 3:
        print("3 post follow through days.")
        schedule.clear()
    elif mycursor.rowcount > 3:
        print("More than 3 post follow through days.")
        schedule.clear()

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

def runAllPostFollowThrough():
    global todayDate
    print(todayDate)
    # if inUptrend == True:
    print("SP500:")
    getSP500Data(todayDate, prev_weekday(todayDate))
    countUpDaysSP500()
    print("Nasdaq:")
    getNasdaqData(todayDate, prev_weekday(todayDate))
    countUpDaysNasdaq()
    print("\n")

    todayDate = next_weekday(todayDate)


schedule.every(3).seconds.do(StartSP500PostFollowThrough)
while 1:
    schedule.run_pending()
    time.sleep(1)

startDate = todayDate + relativedelta(months=-3)
prevWeekday = prev_weekday(todayDate)

print(startDate, "-", todayDate, "\n")
