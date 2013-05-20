import sys
import collections
import threading
import time
#sys.path.append(
from btceapi.btceapi import common
from btceapi.btceapi import trade
from btceapi.btceapi import public
#Value that determins how significant a change must be to make a trade
#If price goes up or down this percent, a sell or buy will be attempted
trade_threshold = 0.006
verbose = 3 #0 = only report trades or attempted trades, 1 = inform of current price 2 = relay all data collected

#set nonce to current time
def new_nonce():
    nonce = int(time.time())
    return nonce
nonce = new_nonce()

#how many seconds to wait before refreshing price
wait = 10

api_key = "56T7XXKD-1FG0B2HV-HLWIKX5M-CB3M8ZUY-8KOJUMWN"
api_secret = "67f91cc69515924bd824614765bb7ed42a186f0acde2c7acb18787845712b4a4"

api = trade.TradeAPI(api_key, api_secret, nonce)

#set what to exchange (i.e. ltc_usd for LTC to USD or btc_ltc for BTC to LTC)
pair = "ltc_btc"
#set these to your pair, (i.e. "btc" for first and "usd" for the second for btc_usd)
curr1 = "balance_ltc"
curr2 = "balance_btc"

#earliest = average_price()
#early = earliest

nonce = time.time()

#gets the last trade price from btc-e
def get_last(pair):
    tickerW = common.makeJSONRequest("/api/2/%s/ticker" % pair)
    ticker = tickerW.get(u'ticker')
    last_price = ticker.get(u'last')
    return last_price
last = float(get_last(pair))

#initializes 10 element list of prices with first last as value for each element
price_list = [last] * 10

#sets current price by averaging last ten results of get_last
def average_price(v = 2):
    #price_list = collections.deque([])
    #price_list.appendleft(last)
    #price_list.append(last)
    #price_list.pop(10)
    average_last = float(sum(price_list))/float(len(price_list))
    #if verbose > 0 and v == 1:
    #    print "last price checked was", average_last
    if verbose > 1 and v == 1:
        print "price list is", price_list
    return average_last

#get balance information, assign balance of first pair to 
def get_balance(get1 = False, get2 = False):
    account_info = vars(api.getInfo())
    bal1 = account_info[curr1]
    bal2 = account_info[curr2]
    if get1 == True:
        return bal1
    if get2 == True:
        return bal2
#get_balance()

def make_trade(trade):
    price = average_price()
    if trade == "buy":
        print "buying 0.1"
        api.trade(pair, "buy", price, 0.1)
    if trade == "sell":
        print "selling 0.1"
        api.trade(pair, "sell", price, 0.1)
#make_trade("sell")

early = average_price()
def check_if_changed(threshold, late):
    global early
    #print early
    print late
    print early, "early"
    buyprice = early + (early*threshold)
    sellprice= early - (early*threshold)
    print "will buy at ", buyprice
    print "will sell at", sellprice
    #late = average_price()
    if average_price() > buyprice:
        print buyprice, "reached"
        late = average_price()
        early = late
        make_trade("buy")
        check_if_changed(trade_threshold, get_last(pair))
        if verbose > 1:
            print "Price threshold updated to", early
    elif average_price() < sellprice:
        print sellprice, "reached"
        late = average_price()
        early = late
        print early, "early"
        make_trade("sell")
        check_if_changed(trade_threshold, get_last(pair))
        print "Price threshold updated to", early
    else:
        print "Not enough change to buy/sell yet"
    if verbose > 0:
        print "last price checked was", average_price()
check_if_changed(trade_threshold, last)
#function to cancel orders that havn't been filled for awhile, not complete
def autocancel():
    orders = api.orderList(pair = pair)
    #print orders
    for o in orders:
        api.cancelOrder(o.order_id)
    if not orders:
        return
#autocancel()

#refreshes every <wait> seconds
def refresh_price():
    threading.Timer(wait, refresh_price).start()
    time.sleep(wait)
    last = float(get_last(pair))
    average_price(1)
    price_list.insert(0, last)
    price_list.pop()
    nonce = new_nonce()
    check_if_changed(trade_threshold, last)
    if verbose > 1:
        print "Last price retrieved was", last
refresh_price()
