from btceapi import trade
from btceapi import public
import sys
import httplib
import urllib
import json
import hashlib
import hmac

#Value that determins how significant a change must be to make a trade
#If value goes up or down this much in USD, a sell or buy will be attempted
trade_threshold = 15
verbose = 0 #0 = only report trades or attempted trades, 1 = inform of new trade info, 2 = relay every trade on the exchange for ltc_usd

first_sale = 0

BTC_api_key = "API KEY HERE"
BTC_api_secret = "API SECRET HERE"

#def update_trade_list():
#    last_tid = getTradeHistory(ltc_usd)
#    print last_tid

pair = "ltc_usd"

print public.getDepth(pair)
#print public.getTradeHistory(pair)


#update_trade_list()
