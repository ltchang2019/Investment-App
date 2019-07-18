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
                price = float(getIntradayHigh(stock))
                if price > tup[1]:
                    listOfNewHighs.append(stock)
                    print(stock, " new high detected at $", price, sep="")
                    checkCorrectionPercentage(stock, tup[2], tup[1])
                    daysBetween(tup[2], todayDate)

def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    difference = abs((d2 - d1).days)
    print((difference), "days since last high.")
    checkLength(difference)

def checkLength(difference):
    if(difference>=35):
        print("Viable flat base length. Check volume % change...")
    else:
        print("Too short for viable base pattern.\n")


def checkCorrectionPercentage(stock, oldHighDate, high):
        oldToNewHighRange = get_data(stock , start_date = oldHighDate, end_date = todayDate)
        rangeLow = oldToNewHighRange.loc[oldToNewHighRange['low'].idxmin()]
        rangeLow = rangeLow['low']
        percentageDifference = ((high - rangeLow)/high) * 100
        percentageDifference = "%.2f" % round(percentageDifference,2)
        print("Correction: ", percentageDifference, "%", sep='')

compareHighs()

#NEXT STEP IS TO CHECK FOR VOLUME SPIKES (40-50%)
