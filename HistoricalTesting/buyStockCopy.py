import mysql.connector

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)
mycursor = mysql.cursor()

def buyStock(symbol, price, date):
    eighPercentBelow = price - (price * .08)
    sql = "INSERT INTO portfolio (symbol, buyPrice, eightPercentBelow, dateBought) VALUES (%s, %s, %s, %s)"
    mycursor.execute(sql, (symbol, price, eighPercentBelow, date))
    mysql.commit()
