from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from IBD25RelativeHighs import StockHighDateList
from IBD25 import symbolList
from datetime import datetime
from GetDateRange import todayDate

def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
    print(abs((d2 - d1).days))

for stock in symbolList:
    for tup in StockHighDateList:
        if tup[0] == stock:
            price = si.get_live_price(stock)
            if price > tup[1]:
                print(stock, "new high detected")
                daysBetween(tup[2], todayDate)



#runtime around 40 seconds
