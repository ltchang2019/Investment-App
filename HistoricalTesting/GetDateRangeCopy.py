from datetime import date, datetime
from dateutil.relativedelta import relativedelta

print("Retrieving date range...")

todayDate = "2018-01-04"
todayDate = datetime.strptime(todayDate, "%Y-%m-%d").date()


startDate = todayDate + relativedelta(months=-3)
startDate = startDate.strftime("%m/%d/%Y")
todayDate = todayDate.strftime("%m/%d/%Y")


print(startDate, "-", todayDate, "\n")
