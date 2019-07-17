from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from IBD25RelativeHighs import StockHighDateList
from IBD25 import symbolList
from datetime import datetime
from GetDateRange import todayDate

listOfNewHighs = list()
def compareHighs():
    print("Retrieving new highs and condition details...")
    for stock in symbolList:
        for tup in StockHighDateList:
            if tup[0] == stock:
                price = si.get_live_price(stock)
                if price > tup[1]:
                    listOfNewHighs.append(stock)
                    print(stock, "new high detected at", price)
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
        print("Viable flat base length.")
    else:
        print("Too short for viable base pattern.\n")

def checkCorrectionPercentage(stock, oldHighDate, high):
        oldToNewHighRange = get_data(stock , start_date = oldHighDate, end_date = todayDate)
        rangeLow = oldToNewHighRange.loc[oldToNewHighRange['low'].idxmin()]
        rangeLow = rangeLow['low']
        percentageDifference = ((high - rangeLow)/high) * 100
        print("Correction: ", percentageDifference, "%", sep='')

compareHighs()

#runtime around 40 seconds
#NEXT STEP: FIND LOW OF RANGE BETWEEN OLD AND NEW HIGH AND MAKE SURE LOW IS NO MORE THAN 15% DECLINE FROM OLD HIGH
