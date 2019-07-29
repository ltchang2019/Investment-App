from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si

price = si.get_live_price("ESNT")
print(price)
