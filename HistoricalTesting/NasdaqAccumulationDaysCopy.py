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
mycursor = mysql.cursor()

sp500 = "^IXIC"
# 1st Day: index closes above last session's price
# 2nd & 3rd Days: low of 1st day is not undercut by new closes
# 4th day (follow through): index closes more than 1% above previous session on high volume

currSP500 = get_data(sp500, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']
currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = todayDate)
pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']
pastSP500Volume= pastSP500.loc[pastSP500['volume'].idxmax()]['volume']

# currSP500Close = 2500
# currSP500Low = 1800
# currSP500Volume = 15000
#
# pastSP500Close = 2000
# pastSP500Volume = 13000

def startFunction():
    sql = "SELECT * FROM NasdaqAccumulationDays"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if mycursor.rowcount == 0:
        firstDay()
    elif mycursor.rowcount > 0:
        middleDays()

def addAccumulationDay():
    sql = "INSERT INTO NasdaqAccumulationDays (Date, close, low, volume) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (todayDate, str(currSP500Close), str(currSP500Low), str(currSP500Volume)))
    mysql.commit()

# ONLY CALL IF TABLE EMPTY
def firstDay():
    if currSP500Close > pastSP500Close:
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
    print(currSP500Close)

    if currSP500Close > firstLow:
         if (currSP500Close - pastSP500Close)/pastSP500Close < .0125:
             addAccumulationDay()
             print("Middle day entered")
         elif (currSP500Close - pastSP500Close)/pastSP500Close > .0125:
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
        truncateNasdaqAccumulationDays = "TRUNCATE TABLE NasdaqAccumulationDays"
        truncateSP500AccumulationDays = "TRUNCATE TABLE SP500AccumulationDays"
        mycursor.execute(truncateNasdaqAccumulationDays)
        mycursor.execute(truncateSP500AccumulationDays)
        mysql.commit()
        print("Low undercut. Rally started over.")

def followThroughDay():
    if currSP500Volume > pastSP500Volume:
        print("Follow through day")
        truncateSP500AccumulationDays = "TRUNCATE TABLE SP500AccumulationDays"
        truncateNasdaqAccumulationDays = "TRUNCATE TABLE NasdaqAccumulationDays"
        mycursor.execute(truncateSP500AccumulationDays)
        mycursor.execute(truncateNasdaqAccumulationDays)
        mysql.commit()
    else:
        print("Follow through volume not satisfied")
        #truncate table, take quarter position signal

startFunction()
