from yahoo_fin.stock_info import *
from IBD25 import symbolList
from GetDateRange import startDate, todayDate

rangeData = get_data('incy' , start_date = startDate , end_date = todayDate, )

rangeDataList = rangeData.high.tolist()
print(max(rangeDataList))
