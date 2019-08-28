from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from SQLSelectTestCopy import getRelativeHigh, getDate
from IBD25Copy import symbolList
from datetime import date, datetime, timedelta
from GetDateRangeCopy import todayDate, prevWeekday
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
from sendSMSCopy import sendMessage
import mysql.connector
from sendHighsToDatabaseCopy import sendNewInfo
import schedule
import time
from dateutil.relativedelta import relativedelta
from get50DayMovingAverage import get50DayMA
from buyStockCopy import buyStock

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor(buffered=True)

def getIntradayHigh(symbol):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = "https://www.nasdaq.com/symbol/" + symbol + "/real-time"
    req = Request(url, headers={'User-Agent': 'Safari/8536.25'})
    html = urlopen(req, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    tags =  soup('span')
    for tag in tags:
        tagID = tag.get('id', None)
        if tagID is None:
            continue
        elif tagID.find('TodaysHigh') >=0:
            return tag.string

# LIST OF NEW HIGH STOCKS ALREADY SENT
alreadySentList = list()

# NEED TO CREATE 5% BUY RANGE COLUMN
listOfNewHighs = list()
def compareHighs():
    print("\nRetrieving new highs and condition details...")
    for stock in symbolList:
        relativeHigh = getRelativeHigh(stock)
        price = getLivePrice(stock)
        date = datetime.strptime(getDate(stock), "%Y-%m-%d").date()
        # if curr price breaks out of relative high, check days between highs, correction percentage, and maybe volume
        if price > relativeHigh:
            listOfNewHighs.append(stock)
            highDifference = price - relativeHigh
            highDifference = "%.2f" % round(highDifference,2)
            print(stock, " new high detected at $", "%.2f" % round(price,2), sep="")
            print("Up by $", highDifference, sep="")
            print("Correction: ", checkCorrectionPercentage(stock, date, relativeHigh), "%", sep='')
            print(daysBetween(date, todayDate), "days since last high.")

            if stock not in alreadySentList:
                # check correction and length for those with corrections less than 15% and at least 5 week long base
                if checkCorrectionPercentage(stock, date, relativeHigh) < 15 and daysBetween(date, todayDate) > 35:
                    movingAverage = get50DayMA(stock, todayDate)
                    currStock = get_data(stock, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
                    currVolume = currStock.loc[currStock['volume'].idxmax()]['volume']
                    volumeSpike = (currVolume - movingAverage)/currVolume
                    if volumeSpike > .4:
                        print("Volume spike: " + str(volumeSpike))
                        print("BUY SIGNAL")
                        print(price)
                        buyStock(stock, price, todayDate)
                    else:
                        addToBreakouts(stock, price, relativeHigh)
                        print(volumeSpike, "percent not enough. Stock added to breakouts list.")
            print("\n")

def addToBreakouts(stock, price, relativeHigh):
    fivePercentAbove = price + (.05 * price)
    buyPoint = relativeHigh + .1
    sql = "INSERT INTO breakouts (symbol, buyPoint, fivePercentAbove) VALUES (%s, %s, %s)"
    mycursor.execute(sql, (stock, buyPoint, fivePercentAbove))
    mysql.commit()

def checkBreakouts():
    sql = "SELECT * FROM breakouts"
    mycursor.execute(sql)
    if mycursor.rowcount > 0:
        results = mycursor.fetchall()
        for row in results:
            stock = row[0]
            buyPoint = row[1]
            fivePercentAbove = row[2]
            currStock = get_data(stock, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
            currPrice = currStock.loc[currStock['close'].idxmax()]['close']
            currVolume = currStock.loc[currStock['volume'].idxmax()]['volume']
            pastStock = get_data(stock, start_date = prevWeekday, end_date = prevWeekday + relativedelta(days=+1))
            pastPrice = pastStock.loc[pastStock['close'].idxmax()]['close']

            if currPrice > buyPoint and currPrice < fivePercentAbove and currPrice > pastPrice and currVolume > get50DayMA(stock, todayDate):
                buyStock(stock, currPrice, todayDate)
                sql = "DELETE FROM breakouts WHERE symbol = %s"
                mycursor.execute(sql, (stock,))
                mysql.commit()
                print(stock, "BOUGHT FROM BREAKOUT LIST.")
            else:
                print(stock, "breakout conditions not met.")
    else:
        print("No items in breakout list.")

    # CHECK FOR STRONG GAIN (AROUND .3%) AND +40% ABOVE AVERAGE VOLUME
    # THEN CHECK THAT STOCK IS BETWEEN BUY POINT AND FIVE PERCENT ABOVE
    # IF CONDITIONS FULFILLED BUY STOCK


def getLivePrice(stock):
    if stock == "KL.TO":
        stock = "KL"
    currStock = get_data(stock, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currStockIntradayHigh = currStock.loc[currStock['high'].idxmax()]['high']

    return currStockIntradayHigh


def daysBetween(d1, d2):
    difference = abs((d2 - d1).days)
    return difference

def checkCorrectionPercentage(stock, oldHighDate, high):
        oldToNewHighRange = get_data(stock , start_date = oldHighDate, end_date = todayDate)
        rangeLow = oldToNewHighRange.loc[oldToNewHighRange['low'].idxmin()]
        rangeLow = rangeLow['low']
        percentageDifference = ((high - rangeLow)/high) * 100
        return percentageDifference

checkBreakouts()
compareHighs()
