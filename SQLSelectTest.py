import mysql.connector
from mysql.connector import Error


try:
   mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

except Error as e :
    print ("Error while connecting to MySQL", e)

def getRelativeHigh(stock):
   mycursor = mysql.cursor()
   query = "SELECT Price FROM RelativeHighList WHERE Symbol = %s"
   mycursor.execute(query, (stock,))
   result = mycursor.fetchall()

   for price in result:
       return price[0]

def getDate(stock):
    mycursor = mysql.cursor()
    query = "SELECT Date FROM RelativeHighList WHERE Symbol = %s"
    mycursor.execute(query, (stock,))
    result = mycursor.fetchall()

    for price in result:
        return price[0]
