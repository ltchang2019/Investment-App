import mysql.connector
from mysql.connector import Error

stock = "PAGS"

try:
   mysql = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "Investment Program"
)

   mycursor = mysql.cursor()
   query = "SELECT Price FROM RelativeHighList WHERE Symbol = %s"
   mycursor.execute(query, (stock,))
   result = mycursor.fetchall()

   result = [row[0] for row in result]
   result = str(result).replace("[", "").replace("]", "")

   print(float(result))

except Error as e :
    print ("Error while connecting to MySQL", e)
