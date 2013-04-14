#NOT Made by mcfundash (me), this is an implementation of btc-e trade API I found and am using as a guide.

# BTC-e trade module takes options, pair the pair being traded eg. ltc_usd, ltc_btc,
# btc_usd. type the type of transaction buy or sell, rate the price you are buying or selling
# at with leading zero if decimal (0.025 not .025), and amount the amount to buy or sell.
#  Usage ./trade.py ltc_btc sell 0.0075 568
# Based on the already existing sample code placed on this site with my additions to make
# a working example.

import sys
import httplib
import urllib
import json
import hashlib
import hmac

# Replace these with your own API key data when generating the key be sure to check the trade
# box.
BTC_api_key = "your-api-key-here"
BTC_api_secret = "your-api-secret-here"

# Reading file to get nonce last used then increment and store for next use.
# You must create the file nonce.txt if first time using the trade api put the number 1 in it.
# It must be in the current directory as you are running the .py file in or change to correct
# path in the open(....).

with open('nonce.txt') as f:
    n = int(f.read()) + 1
f.close()
with open('nonce.txt', 'w') as f:
    f.write(str(n))
f.close()
nonce = n

# method name, options and nonce go into the POST parameters
params = {"method":"Trade",
          "pair" : sys.argv[1] ,
          "type" : sys.argv[2] ,
          "rate" : sys.argv[3] ,
          "amount" : sys.argv[4] ,
          "nonce": nonce}
params = urllib.urlencode(params)

# Hash the params string to produce the Sign header value
H = hmac.new(BTC_api_secret, digestmod=hashlib.sha512)
H.update(params)
sign = H.hexdigest()

headers = {"Content-type": "application/x-www-form-urlencoded",
		   "Key":BTC_api_key,
		   "Sign":sign}
conn = httplib.HTTPSConnection("btc-e.com")
conn.request("POST", "/tapi", params, headers)
response = conn.getresponse()

print response.status, response.reason
print json.load(response)

conn.close()
