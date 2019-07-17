from datetime import date
today = date.today()

print("Retrieving date range...")

todayDate = today.strftime("%m/%d/%Y")

todayList = list(todayDate)

if todayList[0] == "0":
    monthInt = int(todayList[1])
    monthInt = monthInt - 3
    if monthInt < 0:
        monthInt = 12 - monthInt
        todayList[0:2] = str(monthInt)
    else:
        todayList[1] = str(monthInt)
else:
    monthInt = int(todayList[0:2])
    monthInt = monthInt - 3
    todayList[0] = "0"
    todayList[1] = str(monthInt)

startDate = "".join(todayList)

print(startDate, "-", todayDate, "\n")
