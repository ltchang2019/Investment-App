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

print("Retrieving IBD25...")

symbolList = ['COR', 'TTD', 'TEAM', 'PYPL', 'TRU', 'ANET', 'SUPV', 'ODFL', 'PETS', 'CNC', 'ESNT', 'GWRE', 'ALGN', 'THO', 'FOXF', 'CGNX', 'COHR', 'PLNT', 'ALRM', 'BGCP', 'FIVE', 'BABA', 'FB', 'YY', 'STMP', 'RP', 'EDU', 'TAL', 'ATHM', 'PAYC', 'GTN', 'PRAH', 'CBOE', 'AEIS', 'ADI', 'AMAT', 'ICHR', 'KEM', 'LRCX', 'MCHP', 'NVDA', 'OLED', 'ADBE', 'VEEV', 'SINA', 'GRUB']


print(symbolList, "\n")
