#SCRAPE 50 DAY VOLUME MOVING AVERAGE FROM BARCHART.COM
#SCRAPE DAILY VOLUME FROM YAHOO FINANCE
# AVERAGE = DAILY - 50MA / 50MA
import requests
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

stock = "veev"

# FIND 50 DAY VOLUME MOVING AVERAGE
url = "https://www.barchart.com/stocks/quotes/" + stock + "/technical-analysis"
req = Request(url, headers={'User-Agent': 'Safari/8536.25'})
html = urlopen(req, context=ctx).read()
# html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

counter = 1
tags =  soup('td')
for tag in tags:
    if counter == 15:
        string1 = tag.string
        counter = counter + 1
    elif counter<15:
        counter = counter + 1
        continue
    elif counter == 16:
        string2 = tag.string
Average50Volume = string1.replace(string2,"").strip()
Average50Volume = float(Average50Volume.replace(",", ""))

#FIND DAILY VOLUME
url1 = 'https://finance.yahoo.com/quote/' + stock
r = requests.get(url1)
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
        dailyVolume = bigSpan.replace(spanValue,"")
        dailyVolume = float(dailyVolume.replace(",", ""))

percentageChange = ((dailyVolume - Average50Volume)/Average50Volume) * 100
print(percentageChange)
#FAILED CALCULATION... CAN'T FIGURE OUT HOW IBD GETS ITS VOL % CHANGE NUMBERS
