from yahoo_fin import stock_info as si
from IBD25 import symbolList

counter = 0
for stock in symbolList:
    price = si.get_live_price(stock)
    print(symbolList[counter], price)
    counter = counter + 1
