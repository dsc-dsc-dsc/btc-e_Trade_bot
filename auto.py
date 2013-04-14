from btceapi import common
from btceapi import trade
from btceapi import public
import sys
import collections
import threading
import time
#Value that determins how significant a change must be to make a trade
#If value goes up or down this much in USD, a sell or buy will be attempted
trade_threshold = 0.15
verbose = 0 #0 = only report trades or attempted trades, 1 = inform of current price 2 = relay all data collected

#set nonce to current time
nonce = (int(time.time()))

#how many seconds to wait before refreshing price
wait = 1

api_key = "8E9LX6K1-JSN6HS6G-HRH2XM57-X5ULY2FV-QTQHN6XN"
api_secret = "c4556cc5329a6fd74790ca37a48212eddaeec6c34c0b67f0ac9ea59e7c9e9d6d"

api = trade.TradeAPI(api_key, api_secret, nonce)

#set what to exchange (i.e. ltc_usd for LTC to USD or btc_ltc for BTC to LTC)
pair = "ltc_usd"
#set these to your pair, (i.e. "btc" for first and "usd" for the second for btc_usd)
curr1 = "ltc"
curr2 = "usd"

#gets the last trade price from btc-e
def get_last(pair):
    tickerW = common.makeJSONRequest("/api/2/%s/ticker" % pair)
    ticker = tickerW.get(u'ticker')
    last_price = ticker.get(u'last')
    return last_price
last = get_last(pair)

#initializes 10 element list of prices with first last as value for each element
price_list = [last] * 10

#sets current price by averaging last ten results of get_last
def average_price():
    average_last = sum(price_list)/ float(len(price_list))
    #price_list = collections.deque([*])
    #price_list.appendleft(last)
    price_list.insert(0, last)
    price_list.pop()
    if verbose > 0:
        print "last price checked was", average_last
    if verbose > 1:
        print "price list is", price_list

#nonce = time.time()

#refreshes last price every <wait> seconds and adds to price_list
def refresh_price():
    average_price()
    threading.Timer(wait, refresh_price).start()
    last = get_last(pair)
    time.sleep(wait)
    price_list.insert(0, last)
    price_list.pop()
    nonce = (int(time.time()))
    if verbose > 1:
        print "Last price retrieved was", last
refresh_price()

def make_trade():
    #vars()[curr1] = 0
    #vars()[curr2] = 0
    print api.getInfo().toString()
    t = api
    try:
        r = api.getInfo()
        for d in dir():
            if d[:2] == '__':
                continue

            print "    %s: %r" % (d, getattr(r, d))
    except Exception, e:
        print "  An error occurred: %s" % e
    

make_trade()
