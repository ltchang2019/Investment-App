from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from SQLSelectTestCopy import getRelativeHigh, getDate
from IBD25Copy import symbolList
from datetime import datetime
from GetDateRangeCopy import todayDate
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

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)

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

listOfNewHighs = list()
def compareHighs():
    print("Retrieving new highs and condition details...")
    for stock in symbolList:
        relativeHigh = getRelativeHigh(stock)
        price = getLivePrice(stock)
        date = getDate(stock)
        # if curr price breaks out of relative high, check days between, correction percentage, and maybe volume
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
                    currStock = get_data(stock, start_date = todayDate, end_date = datetime.strptime(todayDate, "%m/%d/%Y") + relativedelta(days=+1))
                    currVolume = currStock.loc[currStock['volume'].idxmax()]['volume']
                    volumeSpike = (currVolume - movingAverage)/currVolume
                    if volumeSpike > .4:
                        print(volumeSpike)
                        print("BUY SIGNAL")
            print("\n")

def getLivePrice(stock):
    if stock == "KL.TO":
        stock = "KL"
    currStock = get_data(stock, start_date = todayDate, end_date = datetime.strptime(todayDate, "%m/%d/%Y") + relativedelta(days=+1))
    currStockIntradayHigh = currStock.loc[currStock['high'].idxmax()]['high']

    return currStockIntradayHigh


def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    difference = abs((d2 - d1).days)
    return difference


def checkCorrectionPercentage(stock, oldHighDate, high):
        oldToNewHighRange = get_data(stock , start_date = oldHighDate, end_date = todayDate)
        rangeLow = oldToNewHighRange.loc[oldToNewHighRange['low'].idxmin()]
        rangeLow = rangeLow['low']
        percentageDifference = ((high - rangeLow)/high) * 100
        return percentageDifference

compareHighs()
