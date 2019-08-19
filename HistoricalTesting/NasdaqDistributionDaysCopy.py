from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector
from GetDateRangeCopy import todayDate, prevWeekday
from emergencyDistribution import emergencyCheck

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)

sp500 = "^IXIC"

def checkForDistributionDay():
    # GET CURRENT AND YESTERDAY'S S&P 500 PRICES
    currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500Price = currSP500.loc[currSP500['close'].idxmax()]['close']
    currSP500High = currSP500.loc[currSP500['high'].idxmax()]['high']
    currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
    currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

    pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500Price = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    pastSP500High = pastSP500.loc[pastSP500['high'].idxmax()]['high']
    pastP500Low = pastSP500.loc[pastSP500['low'].idxmax()]['low']
    pastSP500Volume = pastSP500.loc[pastSP500['volume'].idxmax()]['volume']

    # CALCULATE PRICE PERCENTAGE DIFFERENCE
    todayPercentageDiff = ((currSP500Price - pastSP500Price)/pastSP500Price) * 100
    print(todayPercentageDiff)

    # GET YESTERDAY'S VOLUME DATA
    print(pastSP500Volume, currSP500Volume)

    # CHECK IF DIFFERENCE <= -0.2% AND TODAY'S VOLUME > YESTERDAY'S VOLUME BUT IF DECLINE MORE THAN .5% DEFINITELY DISTRIBUTION
    if todayPercentageDiff <= -.5:
        print("Distribution day even though volume is lower")
        addDistributionDay(todayPercentageDiff, currSP500Price, currSP500High, currSP500Low)
    elif todayPercentageDiff <= -0.2 and currSP500Volume > pastSP500Volume:
        print("Distribution day")
        addDistributionDay(todayPercentageDiff, currSP500Price, currSP500High, currSP500Low)
    else:
        print("Not distribution day")

# ADD DISTRIBUTION DAY METHOD
def addDistributionDay(percentageDifference, currSP500Price, currSP500High, currSP500Low):
    sql = "INSERT INTO NasdaqDistributionDays (Date, Correction, close, high, low) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(sql, (todayDate, percentageDifference, currSP500Price, currSP500High, currSP500Low))
    mysql.commit()
    emergencyCheck()

# CHECK DISTRIBUTION DAY COUNT
def checkDayCount():
    sql = "SELECT COUNT(*) FROM NasdaqDistributionDays"
    mycursor.execute(sql)
    dayResult = mycursor.fetchall()[0][0]
    print(dayResult, "distribution days")

    if dayResult >= 4:
        truncatePortfolioAndDistributionDays()
        print("Sell off time")

# CHECK TO REMOVE OLDEST DISTRIBUTION DAY
def checkOldestDay():
    sql = "SELECT Date FROM NasdaqDistributionDays ORDER BY keyIndex ASC LIMIT 1"
    mycursor.execute(sql)
    if mycursor.rowcount > 0:
        oldDate = mycursor.fetchall()[0][0]
        print(oldDate, "last distribution day")
        # if there is at least one distribution day check if it has been on list long enough to remove from count
        if daysBetween(datetime.strptime(oldDate, "%Y-%m-%d").date(), todayDate) >= 35:
            removeSQL = "DELETE FROM NasdaqDistributionDays WHERE Date = %s"
            mycursor.execute(removeSQL, (oldDate,))
            mysql.commit()
            print("Distribution day removed")
    else:
        print("No distribution days in table")

def daysBetween(d1, d2):
    difference = abs((d2 - d1).days)
    return difference

def truncatePortfolioAndDistributionDays():
    truncatePortfolio = "TRUNCATE TABLE portfolio"
    truncateSP500Distribution = "TRUNCATE TABLE SP500DistributionDays"
    truncateNasdaqDistribution = "TRUNCATE TABLE NasdaqDistributionDays"
    mycursor.execute(truncatePortfolio)
    mycursor.execute(truncateSP500Distribution)
    mycursor.execute(truncateNasdaqDistribution)
    mysql.commit()

checkForDistributionDay()
checkOldestDay()
checkDayCount()
