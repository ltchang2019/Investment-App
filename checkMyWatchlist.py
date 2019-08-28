import mysql.connector
from mysql.connector import Error
from yahoo_fin.stock_info import *
from yahoo_fin import stock_info as si
import schedule
import time
from sendWatchlistSMS import sendMessage

try:
   mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

except Error as e :
    print ("Error while connecting to MySQL", e)

cursor = mysql.cursor()

def numberOfElements():
    cursor.execute("select COUNT (*) from myWatchlist")
    result = cursor.fetchall()
    for number in result:
        return number[0]

alreadySent = list()

def checkPrice():
    numberOfChecks = numberOfElements()

    stockPriceList = list()
    count = 1
    while count < (numberOfChecks + 1):
        # GET STOCK SYMBOL OF SINGLE ELEMENT
        symbolQuery = "SELECT Symbol FROM myWatchlist WHERE keyIndex = %s"
        cursor.execute(symbolQuery, (count,))
        symbolResult = cursor.fetchall()
        for symbol in symbolResult:
            symbol = symbol[0]

        # GET TARGET PRICE
        targetPriceQuery = "SELECT targetPrice FROM myWatchlist WHERE keyIndex = %s"
        cursor.execute(targetPriceQuery, (count,))
        targetResult = cursor.fetchall()
        for targetPrice in targetResult:
            targetPrice = targetPrice[0]

        # COMPARE CURRENT PRICE WITH TARGET PRICE AND SEND SMS
        currentPrice = si.get_live_price(symbol)
        if currentPrice > (float(targetPrice) + .1):
            difference = currentPrice - float(targetPrice)
            difference = "%.2f" % round(difference,2)
            print(symbol + " has broken out of target price by $" + str(difference))

            if symbol not in alreadySent:
                sendMessage(symbol, difference)
                alreadySent.append(symbol)

        elif currentPrice < (float(targetPrice) + .1):
            print(symbol, "not broken out.")

        count = count + 1


schedule.every(2).minutes.do(checkPrice)

while 1:
    schedule.run_pending()
    time.sleep(1)
