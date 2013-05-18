import sys
import collections
import threading
import time
#sys.path.append(
from btceapi.btceapi import common
from btceapi.btceapi import trade
from btceapi.btceapi import public
#Value that determins how significant a change must be to make a trade
#If value goes up or down this much in USD, a sell or buy will be attempted
trade_threshold = 0.002
verbose = 2 #0 = only report trades or attempted trades, 1 = inform of current price 2 = relay all data collected

#set nonce to current time
nonce = (int(time.time()))

#how many seconds to wait before refreshing price
wait = 10

api_key = "API KEY HERE"
api_secret = "API SECRET HERE"

api = trade.TradeAPI(api_key, api_secret, nonce)

#set what to exchange (i.e. ltc_usd for LTC to USD or btc_ltc for BTC to LTC)
pair = "ltc_btc"
#set these to your pair, (i.e. "btc" for first and "usd" for the second for btc_usd)
curr1 = "balance_ltc"
curr2 = "balance_btc"

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
    #price_list = collections.deque([])
    #price_list.appendleft(last)
    price_list.append(last)
    price_list.pop(10)
    average_last = float(sum(price_list))/float(len(price_list))
    if verbose > 0 and v == 1:
        print "last price checked was", average_last
    if verbose > 1 and v == 1:
        print "price list is", price_list
    return average_last

earliest = average_price()
early = earliest

nonce = time.time()

#get balance information, assign balance of first pair to 
def get_balance():
    account_info = vars(api.getInfo())
    bal1 = account_info[curr1]
    bal2 = account_info[curr2]
    print bal1, bal2
get_balance()

def make_trade(trade):
    if trade == "buy":
        print "buying 1"
        api.trade(pair, "buy", earliest, 1)
    if trade == "sell":
        print "selling 1"
        api.trade(pair, "sell", earliest, 1)

def check_if_changed(threshold, early, late = average_price()):
    print early
    print late
    print "buying at ", late + threshold
    print "selling at", late - threshold
    late = average_price()
    if early >= late + threshold:
        early = average_price()
        make_trade("buy")
        if verbose > 1:
            print "Price threshold updated to", early
    if early <= late - threshold:
        early = average_price()
        make_trade("buy")
        print "Price threshold updated to", early

#function to cancel orders that havn't been filled for awhile, not complete
def autocancel():
    orders = api.orderList(pair = pair)
    #print orders
    for o in orders:
        api.cancelOrder(o.order_id)
    if not orders:
        return
autocancel()

#refreshes every <wait> seconds
def refresh_price():
    average_price(1)
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
