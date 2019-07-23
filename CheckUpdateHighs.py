from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from IBD25RelativeHighs import StockHighDateList
from IBD25 import symbolList
from datetime import datetime
from GetDateRange import todayDate
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
from sendSMS import sendMessage

#RELATIVE HIGH STORAGE

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
        for tup in StockHighDateList:
            if tup[0] == stock:
                if stock == "KL.TO":
                    stock = "KL"
                price = si.get_live_price(stock)
                if price > tup[1]:
                    listOfNewHighs.append(stock)
                    highDifference = price - tup[1]
                    highDifference = "%.2f" % round(highDifference,2)
                    print(stock, " new high detected at $", "%.2f" % round(price,2), sep="")
                    print("Up by $", highDifference, sep="")
                    print("Correction: ", checkCorrectionPercentage(stock, tup[2], tup[1]), "%", sep='')
                    print(daysBetween(tup[2], todayDate), "days since last high.")
                    sendMessage(stock, "%.2f" % round(price,2), daysBetween(tup[2], todayDate), checkCorrectionPercentage(stock, tup[2], tup[1]), highDifference)

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

compareHighs()

#STORE RELATIVE HIGHS IN NUMPY VARIABLES SO YOU DON'T HAVE TO QUERY THEM EVERY TIME
#ALSO STORE LIST OF WHICH STOCKS HAVE ALREADY HAD +10 CENTS HIGH SO YOU DON'T KEEP RESENDING NOTIFICATIONS
