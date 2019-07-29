from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from SQLSelectTest import getRelativeHigh, getDate
from IBD25 import symbolList
from datetime import datetime
from GetDateRange import todayDate
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
from sendSMS import sendMessage
import mysql.connector
from sendHighsToDatabase import sendNewInfo
import schedule
import time


mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
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

listOfNewHighs = list()
def compareHighs():
    print("Retrieving new highs and condition details...")
    for stock in symbolList:
        relativeHigh = getRelativeHigh(stock)
        price = getLivePrice(stock)
        date = getDate(stock)
        if price > relativeHigh:
            listOfNewHighs.append(stock)
            highDifference = price - relativeHigh
            highDifference = "%.2f" % round(highDifference,2)
            print(stock, " new high detected at $", "%.2f" % round(price,2), sep="")
            print("Up by $", highDifference, sep="")
            print("Correction: ", checkCorrectionPercentage(stock, date, relativeHigh), "%", sep='')
            print(daysBetween(date, todayDate), "days since last high.")
            sendMessage(stock, "%.2f" % round(price,2), daysBetween(date, todayDate), checkCorrectionPercentage(stock, date, relativeHigh), highDifference)

def getLivePrice(stock):
    if stock == "KL.TO":
        stock = "KL"
    price = si.get_live_price(stock)
    return(price)


def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    difference = abs((d2 - d1).days)
    return difference
    checkLength(difference)

def checkLength(dayDifference):
    if(dayDifference>=42):
        print("Viable flat base length. Check volume % change...")
    else:
        print("Too short for viable base pattern.\n")


def checkCorrectionPercentage(stock, oldHighDate, high):
        oldToNewHighRange = get_data(stock , start_date = oldHighDate, end_date = todayDate)
        rangeLow = oldToNewHighRange.loc[oldToNewHighRange['low'].idxmin()]
        rangeLow = rangeLow['low']
        percentageDifference = ((high - rangeLow)/high) * 100
        percentageDifference = "%.2f" % round(percentageDifference,2)
        return percentageDifference


def startChecks():
    schedule.every(1).minutes.do(compareHighs)

def sleep():
    schedule.cancel_job(startChecks)
    time.sleep(43200)

schedule.every().day.at("06:25").do(sendNewInfo)
schedule.every().day.at("06:29").do(startChecks)
schedule.every().day.at("13:00").do(sleep)

while 1:
    schedule.run_pending()
    time.sleep(1)
