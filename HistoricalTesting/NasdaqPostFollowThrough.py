from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector
from GetDateRangeCopy import todayDate, prevWeekday

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)
sp500 = "^IXIC"

currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']

pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = prevWeekday + relativedelta(days=+1))
pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']

def checkForIncrease():
    percentageChange = (currSP500Close - pastSP500Close)/currSP500Close
    if percentageChange > 0:
        sql = "INSERT INTO NasdaqPostFollowThrough (Date, percentChange) VALUES (%s, %s)"
        mycursor.execute(sql, (todayDate, percentageChange))
        mysql.commit()
        print("Increase day entered")
    else:
        print("Restart. Look for accumulation again.")


def countUpDays():
    sql = "SELECT * FROM NasdaqPostFollowThrough"
    mycursor.execute(sql)
    if mycursor.rowcount >= 3:
        print("MARKET IN CONFIRMED UPTREND")
    else:
        checkForIncrease()

countUpDays()
