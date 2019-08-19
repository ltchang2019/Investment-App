import mysql.connector
from yahoo_fin.stock_info import *
from GetDateRangeCopy import todayDate
from dateutil.relativedelta import relativedelta


mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor()

def checkPercentChange():
    query = "SELECT symbol, buyPrice FROM portfolio"
    mycursor.execute(query)
    results = mycursor.fetchall()
    if results != []:
        for row in results:
            symbol = row[0]
            originalPrice = row[1]
            currPrice = getLivePrice(symbol)

            if (originalPrice - currPrice)/originalPrice >= .08:
                print("8% loss triggers sell")
            else:
                print(currPrice, "fine")
    else:
        print("Portfolio empty")

def getLivePrice(stock):
    if stock == "KL.TO":
        stock = "KL"
    currStock = get_data(stock, start_date = todayDate, end_date = todayDate + relativedelta(days=+1))
    currStockIntradayHigh = currStock.loc[currStock['high'].idxmax()]['high']
    return currStockIntradayHigh

checkPercentChange()
