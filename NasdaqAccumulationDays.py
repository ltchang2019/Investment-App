from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)
mycursor = mysql.cursor()

nasdaq = "^IXIC"
today = date.today().strftime('%m/%d/%Y')
prevWeekday = prev_weekday(date.today())

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4:
        adate -= timedelta(days=1)
    return adate

# 1st Day: index closes above last session's price
# 2nd & 3rd Days: low of 1st day is not undercut by new closes
# 4th day (follow through): index closes more than 1% above previous session on high volume

currNasdaq = get_data(nasdaq, start_date = date.today())
currNasdaqClose = currNasdaq.loc[currNasdaq['close'].idxmax()]['close']
currNasdaqLow = currNasdaq.loc[currNasdaq['low'].idxmax()]['low']
currNasdaqVolume = currNasdaq.loc[currNasdaq['volume'].idxmax()]['volume']

pastNasdaq = get_data(nasdaq, start_date = prevWeekday, end_date = date.today())
pastNasdaqClose = pastNasdaq.loc[pastNasdaq['close'].idxmax()]['close']
pastNasdaqVolume= pastNasdaq.loc[pastNasdaq['volume'].idxmax()]['volume']

# currNasdaqClose = 2500
# currNasdaqLow = 1800
# currNasdaqVolume = 15000
#
# pastNasdaqClose = 2000
# pastNasdaqVolume = 13000

def startFunction():
    sql = "SELECT * FROM NasdaqAccumulationDays"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if mycursor.rowcount == 0:
        firstDay()
    elif mycursor.rowcount > 0 and mycursor.rowcount <= 7:
        middleDays()

def addAccumulationDay():
    sql = "INSERT INTO NasdaqAccumulationDays (Date, close, low, volume) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (today, currNasdaqClose, currNasdaqLow, str(currNasdaqVolume)))
    mysql.commit()

# ONLY CALL IF TABLE EMPTY
def firstDay():
    if currNasdaqClose > pastNasdaqClose:
        addAccumulationDay()
        print("First day entered")

# CALL WHEN TABLE HAS AT LEAST ONE ENTRY
def middleDays():
    sql = "SELECT close, low FROM NasdaqAccumulationDays WHERE dayNumber = %s"
    mycursor.execute(sql, (1,))
    result = mycursor.fetchall()
    firstClose = result[0][0]
    firstLow = result[0][1]

    if currNasdaqClose > firstLow:
         if (currNasdaqClose - pastNasdaqClose)/pastNasdaqClose < .017:
             addAccumulationDay()
             print("Middle day entered")
         elif (currNasdaqClose - pastNasdaqClose)/pastNasdaqClose > .017:
            # check that you have at least 3 accumulation days
            sql = "SELECT * FROM NasdaqAccumulationDays WHERE dayNumber = %s"
            mycursor.execute(sql, (3,))
            result = mycursor.fetchall()
            if mycursor.rowcount > 0:
                followThroughDay()
            else:
                print("Haven't had 3rd rally day yet, another middle day added")
    else:
        print("Not accumulation")

def followThroughDay():
    if currNasdaqVolume > pastNasdaqVolume:
        print("Follow through day")
        truncateSQL = "TRUNCATE TABLE NasdaqAccumulationDays"
        mycursor.execute(truncateSQL)
        mysql.commit()
        #truncate table, take quarter position signal

startFunction()
