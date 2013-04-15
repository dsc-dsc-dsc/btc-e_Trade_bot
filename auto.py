from btceapi import common
from btceapi import trade
from btceapi import public
import sys
import collections
import threading
import time
#Value that determins how significant a change must be to make a trade
#If value goes up or down this much in USD, a sell or buy will be attempted
trade_threshold = 0.001
verbose = 2 #0 = only report trades or attempted trades, 1 = inform of current price 2 = relay all data collected

#set nonce to current time
nonce = (int(time.time()))

#how many seconds to wait before refreshing price
wait = 5

api_key = "8E9LX6K1-JSN6HS6G-HRH2XM57-X5ULY2FV-QTQHN6XN"
api_secret = "c4556cc5329a6fd74790ca37a48212eddaeec6c34c0b67f0ac9ea59e7c9e9d6d"

api = trade.TradeAPI(api_key, api_secret, nonce)

#set what to exchange (i.e. ltc_usd for LTC to USD or btc_ltc for BTC to LTC)
pair = "ltc_usd"
#set these to your pair, (i.e. "btc" for first and "usd" for the second for btc_usd)
curr1 = "balance_ltc"
curr2 = "balance_usd"

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
def average_price(v = 2):
    average_last = sum(price_list)/ float(len(price_list))
    #price_list = collections.deque([])
    #price_list.appendleft(last)
    price_list.append(last)
    price_list.pop(10)
    if verbose > 0 and v != 1:
        print "last price checked was", average_last
    if verbose > 1 and v != 1:
        print "price list is", price_list
    return average_last

earliest = average_price(1)
early = earliest

nonce = time.time()

#get balance information, assign balance of first pair to 
def get_balance():
    account_info = vars(api.getInfo())
    bal1 = account_info[curr1]
    bal2 = account_info[curr2]
get_balance()


def check_if_changed(threshold, early, late = average_price(1)):
    print early
    print late
    print late + threshold
    print late - threshold
    late = average_price(1)
    if early >= late + threshold:
        early = average_price()
        print "early has been updated to become", early

    if early <= late - threshold:
        early = average_price()
        print "early has been updated to become", early

#refreshes every <wait> seconds
def refresh_price():
    average_price()
    threading.Timer(wait, refresh_price).start()
    last = get_last(pair)
    time.sleep(wait)
    price_list.insert(0, last)
    price_list.pop()
    nonce = (int(time.time()))
    check_if_changed(trade_threshold, earliest)
    if verbose > 1:
        print "Last price retrieved was", last
refresh_price()
