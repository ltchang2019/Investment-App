from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector
# from GetDateRangeCopy import todayDate, prevWeekday

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor()

sp500 = "^IXIC"
# 1st Day: index closes above last session's price
# 2nd & 3rd Days: low of 1st day is not undercut by new closes
# 4th day (follow through): index closes more than 1% above previous session on high volume
def getNasdaqData(todayDate, prevWeekday):
    getNasdaqData.todayDate = todayDate
    todayDate = getNasdaqData.todayDate

    getNasdaqData.currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500 = getNasdaqData.currSP500
    getNasdaqData.currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']
    getNasdaqData.currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
    getNasdaqData.currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

    getNasdaqData.pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500 = getNasdaqData.pastSP500
    getNasdaqData.pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    getNasdaqData.pastSP500Volume= pastSP500.loc[pastSP500['volume'].idxmax()]['volume']


def startNasdaqFunction():
    sql = "SELECT * FROM NasdaqAccumulationDays"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if mycursor.rowcount == 0:
        firstDay()
    elif mycursor.rowcount > 0:
        middleDays()

def addAccumulationDay():
    sql = "INSERT INTO NasdaqAccumulationDays (Date, close, low, volume) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (getNasdaqData.todayDate, str(getNasdaqData.currSP500Close), str(getNasdaqData.currSP500Low), str(getNasdaqData.currSP500Volume)))
    mysql.commit()

# ONLY CALL IF TABLE EMPTY
def firstDay():
    if getNasdaqData.currSP500Close > getNasdaqData.pastSP500Close:
        addAccumulationDay()
        print("First day entered")
    else:
        print("Failed first day")

# CALL WHEN TABLE HAS AT LEAST ONE ENTRY
def middleDays():
    sql = "SELECT close, low FROM NasdaqAccumulationDays WHERE dayNumber = %s"
    mycursor.execute(sql, (1,))
    result = mycursor.fetchall()
    firstClose = result[0][0]
    firstLow = result[0][1]
    print(getNasdaqData.currSP500Close)

    if getNasdaqData.currSP500Close > firstLow:
         if (getNasdaqData.currSP500Close - getNasdaqData.pastSP500Close)/getNasdaqData.pastSP500Close <= .0125:
             addAccumulationDay()
             print("Middle day entered")
         elif (getNasdaqData.currSP500Close - getNasdaqData.pastSP500Close)/getNasdaqData.pastSP500Close >= .0125:
            # check that you have at least 3 accumulation days
            sql = "SELECT * FROM NasdaqAccumulationDays WHERE dayNumber = %s"
            mycursor.execute(sql, (3,))
            result = mycursor.fetchall()
            if mycursor.rowcount > 0:
                followThroughDay()
            else:
                addAccumulationDay()
                print("Haven't had 3rd rally day yet, another middle day added")
    else:
        truncateSP500AccumulationDays = "TRUNCATE TABLE SP500AccumulationDays"
        truncateNasdaqAccumulationDays = "TRUNCATE TABLE NasdaqAccumulationDays"
        mycursor.execute(truncateSP500AccumulationDays)
        mycursor.execute(truncateNasdaqAccumulationDays)
        mysql.commit()
        print("Low undercut. Rally started over.")

def followThroughDay():
    if getNasdaqData.currSP500Volume > getNasdaqData.pastSP500Volume:
        print("FOLLOW THROUGH DAY")
        truncateSP500AccumulationDays = "TRUNCATE TABLE SP500AccumulationDays"
        truncateNasdaqAccumulationDays = "TRUNCATE TABLE NasdaqAccumulationDays"
        mycursor.execute(truncateSP500AccumulationDays)
        mycursor.execute(truncateNasdaqAccumulationDays)
        mysql.commit()
    else:
        print("Follow through volume not satisfied")
        #truncate table, take quarter position signal
