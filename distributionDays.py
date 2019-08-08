from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import mysql.connector

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

sp500 = "^GSPC"
yesterday = date.today() + relativedelta(days=-1)
today = date.today().strftime('%m/%d/%Y')

def checkForDistributionDay():
    # GET CURRENT AND YESTERDAY'S S&P 500 PRICES
    currSP500Price = si.get_live_price(sp500)
    pastSP500 = get_data(sp500, start_date = yesterday, end_date = date.today())
    pastSP500Price = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    # CALCULATE PRICE PERCENTAGE DIFFERENCE
    todayPercentageDiff = ((currSP500Price - pastSP500Price)/pastSP500Price) * 100
    print(todayPercentageDiff)

    # GET TODAY'S VOLUME DATA
    currSP500Volume = get_data(sp500, start_date = date.today())
    currSP500Volume = currSP500Volume.loc[currSP500Volume['volume'].idxmax()]['volume']
    # GET YESTERDAY'S VOLUME DATA
    pastSP500Volume = pastSP500.loc[pastSP500['volume'].idxmax()]['volume']
    print(pastSP500Volume, currSP500Volume)

    # CHECK IF DIFFERENCE <= -0.2% AND TODAY'S VOLUME > YESTERDAY'S VOLUME
    if todayPercentageDiff <= -0.2 and currSP500Volume > pastSP500Volume:
        print("Distribution day")
        addDistributionDay()
    else:
        print("Not distribution day")

# ADD DISTRIBUTION DAY METHOD
def addDistributionDay():
    mycursor = mysql.cursor()
    sql = "INSERT INTO DistributionDays (Date, Correction) VALUES (%s, %s)"
    mycursor.execute(sql, (today, todayPercentageDiff))
    mysql.commit()

# CHECK DISTRIBUTION DAY COUNT
def checkDayCount():
    mycursor = mysql.cursor()
    sql = "SELECT COUNT(*) FROM DistributionDays"
    mycursor.execute(sql)
    dayResult = mycursor.fetchall()[0][0]
    print(dayResult, "distribution days")

    if dayResult >= 4:
        print("Sell off time")

# CHECK TO REMOVE OLDEST DISTRIBUTION DAY
def checkOldestDay():
    mycursor = mysql.cursor()
    sql = "SELECT Date FROM DistributionDays ORDER BY keyIndex ASC LIMIT 1"
    mycursor.execute(sql)
    oldDate = mycursor.fetchall()[0][0]
    print(oldDate)

    if daysBetween(oldDate, today) >= 35:
        mycursor = mysql.cursor()
        removeSQL = "DELETE FROM DistributionDays WHERE Date = %s"
        mycursor.execute(removeSQL, (oldDate,))
        mysql.commit()
        print("Distribution day removed")

def daysBetween(oldDate, todayDate):
    oldDate = datetime.strptime(oldDate, "%m/%d/%Y")
    todayDate = datetime.strptime(todayDate, "%m/%d/%Y")
    difference = abs((todayDate - oldDate).days)
    return difference

checkForDistributionDay()
checkOldestDay()
checkDayCount()
