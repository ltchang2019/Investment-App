import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://ycharts.com/companies/FFTY/holdings"
req = Request(url, headers={'User-Agent': 'Safari/8536.25'})
html = urlopen(req, context=ctx).read()
# html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')

symbolList = list()
tags =  soup('a')
for tag in tags:
    possibleSymbol = tag.get('href', None)
    if possibleSymbol is None:
        continue
    elif possibleSymbol.find('/companies/') >=0 and tag.string.find(possibleSymbol[11:len(possibleSymbol)]) != -1:
        if possibleSymbol[11:len(possibleSymbol)] != "FFTY":
            symbolList.append(possibleSymbol[11:len(possibleSymbol)])

print(symbolList)
