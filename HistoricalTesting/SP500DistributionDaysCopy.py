from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector
# from SP500EmergencyDistribution import emergencyCheck

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)

sp500 = "^GSPC"
inUptrend = True
def getSP500Data(todayDate, prevWeekday):
    getSP500Data.todayDate = todayDate
    todayDate = getSP500Data.todayDate

    getSP500Data.currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500 = getSP500Data.currSP500
    getSP500Data.currSP500Price = currSP500.loc[currSP500['close'].idxmax()]['close']
    getSP500Data.currSP500High = currSP500.loc[currSP500['high'].idxmax()]['high']
    getSP500Data.currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
    getSP500Data.currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

    getSP500Data.pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500 = getSP500Data.pastSP500
    getSP500Data.pastSP500Price = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    getSP500Data.pastSP500High = pastSP500.loc[pastSP500['high'].idxmax()]['high']
    getSP500Data.pastP500Low = pastSP500.loc[pastSP500['low'].idxmax()]['low']
    getSP500Data.pastSP500Volume = pastSP500.loc[pastSP500['volume'].idxmax()]['volume']

def checkForDistributionDaySP500(todayDate):
    # CALCULATE PRICE PERCENTAGE DIFFERENCE
    todayPercentageDiff = ((getSP500Data.currSP500Price - getSP500Data.pastSP500Price)/getSP500Data.pastSP500Price) * 100
    print(todayPercentageDiff)

    # GET YESTERDAY'S VOLUME DATA
    print(getSP500Data.pastSP500Volume, getSP500Data.currSP500Volume)

    # CHECK IF DIFFERENCE <= -0.2% AND TODAY'S VOLUME > YESTERDAY'S VOLUME BUT IF DECLINE MORE THAN .5% DEFINITELY DISTRIBUTION
    if todayPercentageDiff <= -.5:
        print("Distribution day even if volume is lower")
        addDistributionDay(todayPercentageDiff, getSP500Data.currSP500Price, getSP500Data.currSP500High, getSP500Data.currSP500Low)
    elif todayPercentageDiff <= -0.2 and getSP500Data.currSP500Volume > getSP500Data.pastSP500Volume:
        print("Distribution day")
        addDistributionDay(todayPercentageDiff, getSP500Data.currSP500Price, getSP500Data.currSP500High, getSP500Data.currSP500Low)
    else:
        print("Not distribution day")

# ADD DISTRIBUTION DAY METHOD
def addDistributionDay(percentageDifference, currSP500Price, currSP500High, currSP500Low):
    sql = "INSERT INTO SP500DistributionDays (Date, Correction, close, high, low) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(sql, (getSP500Data.todayDate, str(percentageDifference), str(getSP500Data.currSP500Price), str(getSP500Data.currSP500High), str(getSP500Data.currSP500Low)))
    mysql.commit()
    # emergencyCheck()

# CHECK DISTRIBUTION DAY COUNT
def checkDayCountSP500(todayDate):
    sql = "SELECT COUNT(*) FROM SP500DistributionDays"
    mycursor.execute(sql)
    dayResult = mycursor.fetchall()[0][0]
    print(dayResult, "distribution days")

    if dayResult >= 4:
        truncatePortfolioAndDistributionDays()
        print("SELL OFF TIME")

# CHECK TO REMOVE OLDEST DISTRIBUTION DAY
def checkOldestDaySP500(todayDate):
    sql = "SELECT * FROM SP500DistributionDays ORDER BY keyIndex ASC LIMIT 1"
    mycursor.execute(sql)
    if mycursor.rowcount > 0:
        result = mycursor.fetchall()
        oldDate = result[0][0]
        oldPrice = result[0][2]
        print(oldDate, "last distribution day")
        # if there is at least one distribution day check if it has been on list long enough to remove from count
        if daysBetween(datetime.strptime(oldDate, "%Y-%m-%d").date(), todayDate) >= 35:
            removeOldDistributionDay(oldDate)
            print("Distribution day removed. 35 days passed.")
        elif (getSP500Data.currSP500Price - oldPrice)/oldPrice >= .025:
            removeOldDistributionDay(oldDate)
            print("Distribution day removed. Market climbed 2.5%.")
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
    inUptrend = False

def removeOldDistributionDay(oldDate):
    removeSQL = "DELETE FROM SP500DistributionDays WHERE Date = %s"
    mycursor.execute(removeSQL, (oldDate,))
    mysql.commit()
    print("Distribution day removed")

# checkForDistributionDay()
# checkOldestDay()
# checkDayCount()
