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
    while adate.weekday() > 4:
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

print(currSP500Close)
print(pastSP500Close)
# print(pastSP500)
