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

sp500 = "^GSPC"
today = date.today().strftime('%m/%d/%Y')

def prev_weekday(adate):
    adate -= timedelta(days=1)
    while adate.weekday() > 4: # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate

prevWeekday = prev_weekday(date.today())
print(prevWeekday)
print(date.today())
# 1st Day: index closes above last session's price
# 2nd & 3rd Days: low of 1st day is not undercut
# 4th day (follow through): index closes more than 1% above previous session on high volume

currSP500 = get_data(sp500, start_date = date.today())
currSP500Close = currSP500.loc[currSP500['close'].idxmax()]['close']
currSP500Low = currSP500.loc[currSP500['low'].idxmax()]['low']
currSP500Volume = currSP500.loc[currSP500['volume'].idxmax()]['volume']

pastSP500 = get_data(sp500, start_date = prevWeekday, end_date = date.today())
pastSP500Close = pastSP500.loc[pastSP500['close'].idxmax()]['close']

# currSP500Close = 2500
# currSP500Low = 1800
# currSP500Volume = 15000
#
# pastSP500Close = 2000
# pastSP500Volume = 13000

def startFunction():
    sql = "SELECT * FROM AccumulationDays"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if mycursor.rowcount == 0:
        firstDay()
    elif mycursor.rowcount > 0 and mycursor.rowcount <= 7:
        middleDays()


def addAccumulationDay():
    sql = "INSERT INTO AccumulationDays (Date, close, low, volume) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (today, currSP500Close, currSP500Low, currSP500Volume))
    mysql.commit()

# ONLY CALL IF TABLE EMPTY
def firstDay():
    if currSP500Close > pastSP500Close:
        addAccumulationDay()
        print("First day entered")

# CALL WHEN TABLE HAS AT LEAST ONE ENTRY
def middleDays():
    sql = "SELECT close, low FROM AccumulationDays WHERE dayNumber = %s"
    mycursor.execute(sql, (1,))
    result = mycursor.fetchall()
    firstClose = result[0][0]
    firstLow = result[0][1]

    if currSP500Low > firstLow and (currSP500Close - pastSP500Close)/pastSP500Close < .17:
        addAccumulationDay()
        print("Middle day entered")
    elif currSP500Low > firstLow and (currSP500Close - pastSP500Close)/pastSP500Close > .17:
        # check that you have at least 3 accumulation days
        sql = "SELECT * FROM AccumulationDays WHERE dayNumber = %s"
        mycursor.execute(sql, (3,))
        result = mycursor.fetchall()
        if mycursor.rowcount == 0:
            print("Haven't had 3rd rally day yet")
        else:
            followThroughDay()
    else:
        print("Not accumulation")

def followThroughDay():
    if currSP500Volume > pastSP500Volume:
        print("Follow through day")
        #truncate table, take quarter position signal

# startFunction()
