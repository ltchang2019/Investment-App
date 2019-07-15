import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
import re

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.marketbeat.com/market-data/52-week-highs/"
req = Request(url, headers={'User-Agent': 'Safari/8536.25'})
html = urlopen(req, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

#MAKE LIST OF STOCK SYMBOLS
highList = list()
tags =  soup('a')
for tag in tags:
    possibleSymbol = tag.get('href', None)
    if possibleSymbol is None:
        continue
    elif possibleSymbol.find('/stocks/') >=0 and len(tag.string) < 5:
        highList.append(tag.string)

print(highList)
