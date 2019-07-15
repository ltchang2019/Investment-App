from __future__ import print_function
import time
import intrinio_sdk
from intrinio_sdk.rest import ApiException
from pprint import pprint

intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'OmZkNjU4MTc3NDViODQ1YTNkYjBkYTVmYTRlNDA5OGQ3'

security_api = intrinio_sdk.SecurityApi()

identifier = 'AAPL' # str | A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)
source = '' # str | Return the realtime price from the specified data source. If no source is specified, the best source available is used. (optional)

try:
  api_response = security_api.get_security_realtime_price(identifier, source=source)
  pprint(api_response)
except ApiException as e:
  print("Exception when calling SecurityApi->get_security_realtime_price: %s\r\n" % e)
