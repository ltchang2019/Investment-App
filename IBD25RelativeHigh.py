from yahoo_fin.stock_info import *
from IBD25 import symbolList
from GetDateRange import startDate, todayDate

StockAndHighList = list()
for stock in symbolList:
    rangeData = get_data(stock , start_date = startDate , end_date = todayDate, )
    rangeDataList = rangeData.high.tolist()
    relativeHigh = max(rangeDataList)
    StockAndHighList.append(tuple((stock, relativeHigh)))

print(StockAndHighList)
