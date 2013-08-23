#MUST SET THESE IN ORDER TO HAVE THE BOT WORK
API_KEY=""
API_SECRET=""


#OPTIONAL SETTINGS
#THESE SHOULD BE LEFT TO DEFAULTS UNLESS YOU KNOW WHAT YOU ARE DOING

Trade_Amount=100
#Amount of currency traded/bought each transaction

Threshold=0.006
#Percent of change required to buy/sell.  Default is 0.6%

Sell_Profit=0.02

Pair="ftc_btc"
#Currency pair to trade in, may be set to anything listed on btc-e

Refresh=15
#How often to refresh in seconds

Simulation="off"
#set to either "on" or "off" (off be default)

Verbosity=5
#How verbose the porgram is, somewhat broken at the moment,
#will be perfected in later releases
