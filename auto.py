import time
import datetime
import config
import os
import logging
from btceapi.btceapi import common
from btceapi.btceapi import trade
from btceapi.btceapi import public
from configobj import ConfigObj

#Value that determines how significant a change must be to make a trade
#If price goes up or down this percent, a sell or buy will be attempted
trade_threshold = config.Threshold

#0 = only report trades or attempted trades, 1 = inform of current price 2 = relay all data collected
verbose = config.Verbosity 

#Amount to trade at
tradex = config.Trade_Amount

SimMode = config.Simulation

#Minimum profit in percent 
sell_profit = config.Sell_Profit
#how many seconds to wait before refreshing price
wait = config.Refresh

errlog = 'Errorlog.txt'
logging.basicConfig(filename=errlog, level=logging.DEBUG,)
logging.debug('Logfile working correctly')
api_key = config.API_KEY
api_secret = config.API_SECRET

#currency pairing i.e. btc/usd, btc/ltc etc.
pair = config.Pair

#set these to your pair, (i.e. "btc" for first and "usd" for the second for btc_usd)
curr1 = 'balance_'
curr1 += pair[:3]
curr2 = 'balance_'
curr2 += pair[4:]

#functions for loading and saving last actions and buy/sell price 
def saved_action():
    state = ConfigObj('saved_state.ini')
    lastaction = state['last_action']
    return lastaction

def saved_price():
    state = ConfigObj('saved_state.ini')		
    lastprice = state['last_price']
    return lastprice
	
def save_state(action,price):
    save = ConfigObj('saved_state.ini')
    save['last_action'] = action
    save['last_price'] = price
    save.write()

#returns smallest amount after a buy to make a profitable sell
def calc_profit():
    profit = float(saved_price()) + (float(saved_price()) * float(sell_profit))
    return profit

#Resets current action in case of an autocancel
def revert_on_cancel():
    revert =  ConfigObj('saved_state.ini')
    revert['last_price'] =  revert['old_price']
    revert['last_action'] =  revert['old_action']
    revert.write()

#Saves the last action and price for autocancel
def save_old():
    saveold =  ConfigObj('saved_state.ini')
    saveold['old_price'] = saveold['last_price']
    saveold['old_action'] = saveold['last_action']
    saveold.write()
				
#earliest = average_price()
#early = earliest

if SimMode == "off":
    print "Simulation off"
elif SimMode == "on":
    print "Simulation on"
else:
    print "Simulation not correctly set, please check config file"
    exit()

#set nonce to current time
def new_nonce():
    nonce = int(time.time())
    return nonce
nonce = new_nonce()

#BTC-E API access setup
api = trade.TradeAPI(api_key, api_secret, nonce)

#gets the last trade price from btc-e
def get_last(pair):
    tickerW = common.makeJSONRequest("/api/2/%s/ticker" % pair)
    ticker = tickerW.get(u'ticker')
    last_price = ticker.get(u'last')
    return last_price

last = float(get_last(pair))
#initializes LIST_SIZE-element list of prices with first last as value for each element
LIST_SIZE = 20
price_list = [last] * LIST_SIZE

#sets current price by averaging last LIST_SIZE results of get_last
def average_price(v = 2):
    average_last = float(sum(price_list))/float(len(price_list))
    if verbose > 1 and v == 1:
        print "******************************************************************************************"
        print price_list[:10]
        print price_list[10:]
    return average_last

#get balance information, assign balance of first pair to 
def get_balance(get):
    account_info = vars(api.getInfo())
    bal1 = account_info[curr1]
    bal2 = account_info[curr2]
    if SimMode == "on":
        return 99999
    if get == 1:
        return bal1
    if get == 2:
        return bal2

def make_trade(trade, tradex = tradex):
    TLog = open('TradeLog.txt', 'a')
    price = average_price()
    tradeInfo = str(trade) +","+  str(price)
    tradeInfo = str(tradeInfo) + "\n"
    print tradeInfo
    if trade == "buy":
        print "buying", tradex
        if SimMode == "off":
	    save_old()
	    api.trade(pair, "buy", price, tradex)
        TLog.write(tradeInfo)
	save_state("buy",price)
        print "writing", tradeInfo
        TLog.close()
    if trade == "sell":
        print "selling", tradex
        print "writing", tradeInfo
        if SimMode == "off":
	    save_old()
	    api.trade(pair, "sell", price, tradex)
	TLog.write(tradeInfo)
	save_state("sell",price)
	print "writing", tradeInfo
	TLog.close()

early = average_price()
def check_if_changed(threshold, late):
    global early
    buyprice = early - (early*threshold)
    sellprice= early + (early*threshold) + (early*0.001)
    if verbose > 0:
        print "BUYING  ===", buyprice
        print "SELLING ===", sellprice
    if average_price() < buyprice:
        print buyprice, "reached"
        #if get_balance(2) < tradex*average_price():
            #print float(tradex)*float(average_price())-float(get_balance(2)), "needed to buy"
            #return
        late = average_price()
        early = late
	print "ready to buy, Last action was:", saved_action()
        if saved_action() == "sell":
	    if get_balance(2) > tradex*average_price():
               make_trade("buy")
	    else :
	       print float(tradex)*float(average_price())-float(get_balance(2)), "needed to buy"	 	
	else :
	   print "Failed to buy"
        check_if_changed(trade_threshold, get_last(pair))
        if verbose > 1:
            print "Price threshold updated to", early
    elif average_price() > sellprice:
        print sellprice, "reached"
        # if get_balance(1) < tradex:
           #"print float(tradex)-float(get_balance(1)), "needed to sell"
            #return
        late = average_price()
        early = late
        print early, "early"
	print "ready to sell, Last action was:", saved_action()
        if saved_action() == "buy" and calc_profit() <= sellprice:
  	   if get_balance(1) > tradex:        
	      make_trade("sell")
	   else :
	      print float(tradex)-float(get_balance(1)), "needed to sell"		
	else :
           print "Failed to sell"
        check_if_changed(trade_threshold, get_last(pair))
        print "Price threshold updated to", early
#    else:
#        print "Not enough change to buy/sell yet"
    if verbose > 0:
        print "AVERAGE ===", average_price()

#function to cancel orders that havn't been filled for awhile, not complete
#Work in progress, not sure if I'll even end up implementing it at all
def autocancel():
    if SimMode == "on":
        return
    ORDER_TIMEOUT = 180
    current_time = datetime.datetime.now()
    try:
        orders = api.orderList(pair = pair)
    except Exception:
        return
    if not orders:
        return
    if len(orders) > 0:
        print "%d outstanding orders" % len(orders)
    order_ages = []
    for o in orders:
        order_ages.append([o.order_id, current_time - o.timestamp_created])
    for order in order_ages:
        if order[1].seconds > ORDER_TIMEOUT:
            print "Cancelling", order[0]
            api.cancelOrder(order[0])
	    revert_on_cancel()		
					
#refreshes every <wait> seconds
def refresh_price():
    print "\n" * 100		
    last = float(get_last(pair))
    average_price(1)
    price_list.insert(0, last)
    price_list.pop()
    nonce = new_nonce()
    autocancel()
    check_if_changed(trade_threshold, last)
    if verbose > 1:
        print "CURRENT ===", last
	print "BALANCE:", pair[:3],get_balance(1),"/",pair[4:],get_balance(2)
	print "LAST ACTION", saved_action(), "@", saved_price()
	if saved_action() == "buy":
	   print "Next profitable sell @", calc_profit()	 

while True:
   time.sleep(wait)
   try:
        refresh_price()
   except Exception:
        try:
            err
        except:
            err = "000"
        print "Something went wrong! Could not connect to BTC-E! Error Code", err
        logging.exception('Got exception on main handler')
        time.sleep(60)
        continue	
    
