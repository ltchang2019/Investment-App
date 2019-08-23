from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)
sp500 = "^GSPC"

def getSP500Data(todayDate, prevWeekday):
    getSP500Data.todayDate = todayDate
    todayDate = getSP500Data.todayDate

    getSP500Data.currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500 = getSP500Data.currSP500
    getSP500Data.currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']

    getSP500Data.pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = prevWeekday + relativedelta(days=+1))
    pastSP500 = getSP500Data.pastSP500
    getSP500Data.pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']

def checkForIncrease(daysUp, daysDown):
    percentageChange = (getSP500Data.currSP500Close - getSP500Data.pastSP500Close)/getSP500Data.currSP500Close
    # sql = "SELECT * FROM SP500PostFollowThrough"
    # mycursor.execute(sql)
    if percentageChange > 0:
        sql = "INSERT INTO SP500PostFollowThrough (Date, percentChange, upOrDown) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (getSP500Data.todayDate, percentageChange, "increase"))
        mysql.commit()
        print("Increase day entered")
        if daysUp >= 1:
            print("MARKET IN CONFIRMED UPTREND")
            truncatePostFollowThroughTables()
    elif percentageChange < 0:
        sql = "INSERT INTO SP500PostFollowThrough (Date, percentChange, upOrDown) VALUES (%s, %s, %s)"
        mycursor.execute(sql, (getSP500Data.todayDate, percentageChange, "decrease"))
        mysql.commit()
        if daysDown >= 1:
            print("Second down day. Restart rally.")
            truncatePostFollowThroughTables()
        else:
            print("First down day but hasn't been 3 days yet.")


def countUpDaysSP500():
    sql = "SELECT upOrDown FROM SP500PostFollowThrough"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    upCounter = 0
    downCounter = 0
    for upDown in results:
        if upDown[0] == "increase":
            upCounter += 1
        elif upDown[0] == "decrease":
            downCounter += 1

    if upCounter >= 2:
        truncatePostFollowThroughTables()
        print("2 of 3 days up. MARKET IN CONFIRMED UPTREND")
    elif downCounter >= 2:
        truncatePostFollowThroughTables()
        print("2 of 3 days down. Restart rally.")
    else:
        checkForIncrease(upCounter, downCounter)
        # condition: less than 2 up days and less than 2 down days

def truncatePostFollowThroughTables():
    truncateSP500PostFollowThrough = "TRUNCATE TABLE SP500PostFollowThrough"
    truncateNasdaqPostFollowThrough = "TRUNCATE TABLE NasdaqPostFollowThrough"
    mycursor.execute(truncateSP500PostFollowThrough)
    mycursor.execute(truncateNasdaqPostFollowThrough)
    mysql.commit()
