from yahoo_fin import stock_info as si
from IBD25 import symbolList

for stock in symbolList:
    price = si.get_live_price(stock)
    print(price)
