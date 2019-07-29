import mysql.connector
from IBD25RelativeHighs import StockHighDateList

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

def sendNewInfo():
    mycursor = mysql.cursor()
    truncateSQL = "TRUNCATE TABLE RelativeHighList"
    mycursor.execute(truncateSQL)
    mysql.commit()

    sql = "INSERT INTO RelativeHighList (Symbol, Price, Date) VALUES (%s, %s, %s)"

    for tup in StockHighDateList:
        mycursor.execute(sql, (tup[0], tup[1], tup[2]))
        mysql.commit()

    print("Data submitted!")
