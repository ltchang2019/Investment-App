import mysql.connector
from IBD25RelativeHighsCopy import StockHighDateList

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "HistoricalTesting"
)

def sendNewInfo():
    mycursor = mysql.cursor()
    truncateSQL = "TRUNCATE TABLE HistoricalRelativeHighList"
    mycursor.execute(truncateSQL)
    mysql.commit()

    sql = "INSERT INTO HistoricalRelativeHighList (Symbol, Price, Date) VALUES (%s, %s, %s)"

    for tup in StockHighDateList:
        mycursor.execute(sql, (tup[0], tup[1], tup[2]))
        mysql.commit()

    print("Data submitted!")

sendNewInfo()
