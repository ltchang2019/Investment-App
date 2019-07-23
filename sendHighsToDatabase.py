import mysql.connector
from IBD25RelativeHighs import StockHighDateList

mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

mycursor = mysql.cursor()
sql = "Insert into RelativeHighList(Symbol, Price, Date) values (%s, %s, %s)"

for tup in StockHighDateList:
    val = (tup[0], tup[1], tup[2])
    mycursor.execute(sql, val)
    mysql.commit()

print("Data submitted")
