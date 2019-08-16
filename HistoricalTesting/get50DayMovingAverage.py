from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import mysql.connector


def get50DayMA(stock, todayDate):
    stockInfo = get_data(stock, start_date = todayDate + relativedelta(days=-70), end_date = todayDate)
    total = stockInfo['volume'].sum()
    average = total/50
    return average
