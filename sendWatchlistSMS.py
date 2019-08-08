# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

def sendMessage(symbol, difference):
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'ACe5c6e04f0dbf0e57b43e4fac75994b95'
    auth_token = '1c4d48168b7949c6034749f0c6b68a16'
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body= symbol + " has broken out of target price by $" + str(difference),
                         from_='+16199401564',
                         to='+18583545880'
                     )
    print("Sent message!")
