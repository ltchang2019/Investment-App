import requests
from bs4 import BeautifulSoup
url = 'https://finance.yahoo.com/quote/' +
r = requests.get(url)
soup = BeautifulSoup(r.text, features="lxml")

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

counter = 1
for span in soup.findAll("span"):
    spanValue = span.get_text()
    if hasNumbers(spanValue) and spanValue.find(",") >= 0 and spanValue.find(".") < 0:
        bigSpan = spanValue
        counter = counter + 1
    elif counter < 5:
        counter = counter + 1
    elif(counter == 6):
        finalValue = bigSpan.replace(spanValue,"")
        print(finalValue)
