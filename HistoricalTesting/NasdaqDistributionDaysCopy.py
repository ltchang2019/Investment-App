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

sp500 = "^IXIC"
inUptrend = True
def getNasdaqData(todayDate, prevWeekday):
    getNasdaqData.todayDate = todayDate
    todayDate = getNasdaqData.todayDate

    getNasdaqData.currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500 = getNasdaqData.currSP500
    getNasdaqData.currSP500Price = currSP500.loc[currSP500['close'].idxmax()]['close']
    getNasdaqData.currSP500High = currSP500.loc[currSP500['high'].idxmax()]['high']
    getNasdaqData.currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
    getNasdaqData.currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

    getNasdaqData.pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500 = getNasdaqData.pastSP500
    getNasdaqData.pastSP500Price = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    getNasdaqData.pastSP500High = pastSP500.loc[pastSP500['high'].idxmax()]['high']
    getNasdaqData.pastP500Low = pastSP500.loc[pastSP500['low'].idxmax()]['low']
    getNasdaqData.pastSP500Volume = pastSP500.loc[pastSP500['volume'].idxmax()]['volume']

def checkForDistributionDayNasdaq(todayDate):
    # CALCULATE PRICE PERCENTAGE DIFFERENCE
    todayPercentageDiff = ((getNasdaqData.currSP500Price - getNasdaqData.pastSP500Price)/getNasdaqData.pastSP500Price) * 100
    print(todayPercentageDiff)

    # GET YESTERDAY'S VOLUME DATA
    print(getNasdaqData.pastSP500Volume, getNasdaqData.currSP500Volume)

    # CHECK IF DIFFERENCE <= -0.2% AND TODAY'S VOLUME > YESTERDAY'S VOLUME BUT IF DECLINE MORE THAN .5% DEFINITELY DISTRIBUTION
    if todayPercentageDiff <= -.5:
        print("Distribution day even if volume is lower")
        addDistributionDay(todayPercentageDiff, getNasdaqData.currSP500Price, getNasdaqData.currSP500High, getNasdaqData.currSP500Low)
    elif todayPercentageDiff <= -0.2 and getNasdaqData.currSP500Volume > getNasdaqData.pastSP500Volume:
        print("Distribution day")
        addDistributionDay(todayPercentageDiff, getNasdaqData.currSP500Price, getNasdaqData.currSP500High, getNasdaqData.currSP500Low)
    else:
        print("Not distribution day")

# ADD DISTRIBUTION DAY METHOD
def addDistributionDay(percentageDifference, currSP500Price, currSP500High, currSP500Low):
    sql = "INSERT INTO NasdaqDistributionDays (Date, Correction, close, high, low) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(sql, (getNasdaqData.todayDate, str(percentageDifference), str(getNasdaqData.currSP500Price), str(getNasdaqData.currSP500High), str(getNasdaqData.currSP500Low)))
    mysql.commit()
    # emergencyCheck()

# CHECK DISTRIBUTION DAY COUNT
def checkDayCountNasdaq(todayDate):
    sql = "SELECT COUNT(*) FROM NasdaqDistributionDays"
    mycursor.execute(sql)
    dayResult = mycursor.fetchall()[0][0]
    print(dayResult, "distribution days")

    if dayResult >= 4:
        truncatePortfolioAndDistributionDays()
        print("SELL OFF TIME")

# CHECK TO REMOVE OLDEST DISTRIBUTION DAY
def checkOldestDayNasdaq(todayDate):
    sql = "SELECT * FROM NasdaqDistributionDays ORDER BY keyIndex ASC LIMIT 1"
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
        elif (getNasdaqData.currSP500Price - oldPrice)/oldPrice >= .05:
            removeOldDistributionDay(oldDate)
            print("Distribution day removed. Market climbed 5%.")
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
    removeSQL = "DELETE FROM NasdaqDistributionDays WHERE Date = %s"
    mycursor.execute(removeSQL, (oldDate,))
    mysql.commit()
    print("Distribution day removed. Been 35 days.")

# checkForDistributionDay()
# checkOldestDay()
# checkDayCount()
