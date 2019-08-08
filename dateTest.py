from datetime import date
from dateutil.relativedelta import relativedelta

threeMonthsAgo = date.today() + relativedelta(months=-3)

print(threeMonthsAgo.strftime("%m/%d/%Y"))
