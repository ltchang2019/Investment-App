from datetime import date
from dateutil.relativedelta import relativedelta
today = date.today()

print("Retrieving date range...")

todayDate = today.strftime("%m/%d/%Y")

startDate = date.today() + relativedelta(months=-3)
startDate = startDate.strftime("%m/%d/%Y")

print(startDate, "-", todayDate, "\n")
