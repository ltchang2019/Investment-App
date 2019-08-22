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

sp500 = "^GSPC"
# 1st Day: index closes above last session's price
# 2nd & 3rd Days: low of 1st day is not undercut by new closes
# 4th day (follow through): index closes more than 1% above previous session on high volume
def getSP500Data(todayDate, prevWeekday):
    getSP500Data.todayDate = todayDate
    todayDate = getSP500Data.todayDate

    getSP500Data.currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currSP500 = getSP500Data.currSP500
    getSP500Data.currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']
    getSP500Data.currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
    getSP500Data.currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

    getSP500Data.pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
    pastSP500 = getSP500Data.pastSP500
    getSP500Data.pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']
    getSP500Data.pastSP500Volume= pastSP500.loc[pastSP500['volume'].idxmax()]['volume']


def startSP500Function():
    sql = "SELECT * FROM SP500AccumulationDays"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if mycursor.rowcount == 0:
        firstDay()
    elif mycursor.rowcount > 0:
        middleDays()

def addAccumulationDay():
    sql = "INSERT INTO SP500AccumulationDays (Date, close, low, volume) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (getSP500Data.todayDate, str(getSP500Data.currSP500Close), str(getSP500Data.currSP500Low), str(getSP500Data.currSP500Volume)))
    mysql.commit()

# ONLY CALL IF TABLE EMPTY
def firstDay():
    if getSP500Data.currSP500Close > getSP500Data.pastSP500Close:
        addAccumulationDay()
        print("First day entered")
    else:
        print("Failed first day")

# CALL WHEN TABLE HAS AT LEAST ONE ENTRY
def middleDays():
    sql = "SELECT close, low FROM SP500AccumulationDays WHERE dayNumber = %s"
    mycursor.execute(sql, (1,))
    result = mycursor.fetchall()
    firstClose = result[0][0]
    firstLow = result[0][1]
    print(getSP500Data.currSP500Close)

    if getSP500Data.currSP500Close > firstLow:
         if (getSP500Data.currSP500Close - getSP500Data.pastSP500Close)/getSP500Data.pastSP500Close <= .0125:
             addAccumulationDay()
             print("Middle day entered")
         elif (getSP500Data.currSP500Close - getSP500Data.pastSP500Close)/getSP500Data.pastSP500Close >= .0125:
            # check that you have at least 3 accumulation days
            sql = "SELECT * FROM SP500AccumulationDays WHERE dayNumber = %s"
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
    if getSP500Data.currSP500Volume > getSP500Data.pastSP500Volume:
        print("FOLLOW THROUGH DAY")
        truncateSP500AccumulationDays = "TRUNCATE TABLE SP500AccumulationDays"
        truncateNasdaqAccumulationDays = "TRUNCATE TABLE NasdaqAccumulationDays"
        mycursor.execute(truncateSP500AccumulationDays)
        mycursor.execute(truncateNasdaqAccumulationDays)
        mysql.commit()
    else:
        print("Follow through volume not satisfied")
        #truncate table, take quarter position signal
