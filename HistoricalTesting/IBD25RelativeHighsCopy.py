from yahoo_fin.stock_info import *
import pandas as pd
import numpy as np
from IBD25Copy import symbolList
from GetDateRangeCopy import startDate, todayDate
from datetime import datetime

print("Retrieving relative highs and dates...")

StockHighDateList = list()
for stock in symbolList:
    rangeData = get_data(stock , start_date = startDate , end_date = todayDate)
    highPriceData = rangeData.loc[rangeData['high'].idxmax()]

    highDate = highPriceData.name
    StockHighDateList.append(tuple(((highPriceData['ticker'], highPriceData['high'], highDate))))

print(StockHighDateList, "\n")
#creates list of all stocks data with format: (symbol, high, date)
