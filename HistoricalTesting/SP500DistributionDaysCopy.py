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

sp500 = "^GSPC"

def checkForDistributionDay():
    # GET CURRENT AND YESTERDAY'S S&P 500 PRICES
    currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500Price = currSP500.loc[currSP500['close'].idxmax()]['close']
    currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']
    pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500Price = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    pastSP500Volume = pastSP500.loc[pastSP500['volume'].idxmax()]['volume']

    # CALCULATE PRICE PERCENTAGE DIFFERENCE
    todayPercentageDiff = ((currSP500Price - pastSP500Price)/pastSP500Price) * 100
    print(todayPercentageDiff)

    # GET YESTERDAY'S VOLUME DATA
    print(pastSP500Volume, currSP500Volume)

    # CHECK IF DIFFERENCE <= -0.2% AND TODAY'S VOLUME > YESTERDAY'S VOLUME
    if todayPercentageDiff <= -0.2 and currSP500Volume > pastSP500Volume:
        print("Distribution day")
        addDistributionDay(todayPercentageDiff)
    else:
        print("Not distribution day")

# ADD DISTRIBUTION DAY METHOD
def addDistributionDay(percentageDifference):
    sql = "INSERT INTO SP500DistributionDays (Date, Correction) VALUES (%s, %s)"
    mycursor.execute(sql, (todayDate, percentageDifference))
    mysql.commit()

# CHECK DISTRIBUTION DAY COUNT
def checkDayCount():
    sql = "SELECT COUNT(*) FROM SP500DistributionDays"
    mycursor.execute(sql)
    dayResult = mycursor.fetchall()[0][0]
    print(dayResult, "distribution days")

    if dayResult >= 4:
        print("Sell off time")

# CHECK TO REMOVE OLDEST DISTRIBUTION DAY
def checkOldestDay():
    sql = "SELECT Date FROM SP500DistributionDays ORDER BY keyIndex ASC LIMIT 1"
    mycursor.execute(sql)
    if mycursor.rowcount > 0:
        oldDate = mycursor.fetchall()[0][0]
        print(oldDate, "last distribution day")
        # if there is at least one distribution day check if it has been on list long enough to remove from count
        if daysBetween(datetime.strptime(oldDate, "%Y-%m-%d").date(), todayDate) >= 35:
            removeSQL = "DELETE FROM SP500DistributionDays WHERE Date = %s"
            mycursor.execute(removeSQL, (oldDate,))
            mysql.commit()
            print("Distribution day removed")
    else:
        print("No distribution days in table")


def daysBetween(d1, d2):
    difference = abs((d2 - d1).days)
    return difference

checkForDistributionDay()
checkOldestDay()
checkDayCount()
