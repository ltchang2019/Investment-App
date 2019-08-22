from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector
from GetDateRangeCopy import todayDate, prev_weekday

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)
sp500 = "^GSPC"

fourDaysAgo = prev_weekday(prev_weekday(prev_weekday(prev_weekday(todayDate))))
threeDaysAgo = prev_weekday(prev_weekday(prev_weekday(todayDate)))
twoDaysAgo = prev_weekday(prev_weekday(todayDate))
oneDayAgo = prev_weekday(todayDate)

dropDays = 0

def checkTwoDays(theDay, pastDay):
    global dropDays

    currSP500 = get_data(sp500, start_date = theDay, end_date = theDay + relativedelta(days=+1))
    currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']

    pastSP500 = get_data(sp500, start_date = pastDay, end_date = theDay)
    pastSP500High = pastSP500.loc[pastSP500['high'].idxmax()]['high']

    if (pastSP500High - currSP500Low)/pastSP500High >= .025:
        dropDays += 1

def emergencyCheck():
    global dropDays
    checkTwoDays(todayDate, oneDayAgo)
    checkTwoDays(oneDayAgo, twoDaysAgo)
    checkTwoDays(twoDaysAgo, threeDaysAgo)
    checkTwoDays(threeDaysAgo, fourDaysAgo)

    if dropDays >= 2:
        truncatePortfolio = "TRUNCATE TABLE portfolio"
        truncateSP500Distribution = "TRUNCATE TABLE SP500DistributionDays"
        truncateNasdaqDistribution = "TRUNCATE TABLE NasdaqDistributionDays"
        mycursor.execute(truncatePortfolio)
        mycursor.execute(truncateSP500Distribution)
        mycursor.execute(truncateNasdaqDistribution)
        mysql.commit()
        print("EMERGENCY SELL OFF")
