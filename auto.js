//value that determines if a change in price is significant enough to make a trade
//If the price changes this much in USD, the bot will attempt to buy/sell accordingly
var trade_threshold = 0.20,
    verbose = 1; //0 = only report trades and attempts, 1 = inform of new trade-history info, 2 = relay each individual trade

var first_sale = 0;

var BTCE = require('btc-e');

var apiKey = 'YOUR API KEY HERE',
    secret = 'YOUR SECRET HERE';

var btce = new BTCE(apiKey, secret);

var trade_list = [];

function update_trade_list() {
  var last_tid;
  last_tid = (trade_list.length > 1) ? trade_list.slice(-1)[0].tid : 0;
  if (verbose > 0) {
    console.log("Trades recorded: " + trade_list.length + ' @(' + last_tid + ')');
  }
  try {
    btce.trades('ltc_usd', function(err, data) {
      data.reverse();
      for (var i = 0; i < data.length; ++i) {
        if (data[i].tid > last_tid) {
          trade_list.push({"price":data[i].price, "tid":data[i].tid});
          if (verbose > 1) {
            console.log("Got " + data[i].tid);
          }
        }
      }
    });
  } catch(e) {
    console.log("### API CONNECTION ERROR (0) ###");
    console.log(e);
  }
};

function make_trade(transaction, rate) {
  var usd = 0,
      ltc = 0;
  btce.getInfo(function(err, data) {
    usd = data.funds.usd;
    ltc = data.funds.ltc;
    if (transaction == "buy") {
      if(usd > rate) {
        btce.trade('ltc_usd', 'buy', rate, 1, function() {
          console.log("Bought 1 LTC for " + rate.toFixed(4));
        });
      } else {
        console.log("Wanted to buy at " + rate.toFixed(4) + " but no funds ;_;");
      }
    }
    else if (transaction == "sell" && rate > first_sale) {
      if (ltc > 1) {
        btce.trade('ltc_usd', 'sell', rate, 1, function() {
          console.log("Sold 1 LTC for " + rate.toFixed(4));
        });
      } else {
        console.log("Wanted to sell at " + rate.toFixed(4) + " but no coins ;_;");
      }
      first_sale = 0;
    }
  });
  trade_list = [{"price":trade_list.slice(-1)[0].price, "tid":trade_list.slice(-1)[0].tid}]
};

function check_if_changed(threshold) {
  var earliest = 0,
      latest = 0;
  for (var i = 0; i < 10; ++i) {
    earliest += trade_list[i].price;
  }
  earliest = earliest / 10;
  for (var i = 0; i < 10; ++i) {
    latest += trade_list.slice(-(1 + i))[0].price;
  }
  latest = latest / 10;

  var change = Math.abs(latest - earliest)
  if (change > threshold) {
    if (latest > earliest) {
      make_trade('sell', latest);
    }
    else if (earliest > latest) {
      make_trade('buy', latest);
    }
  } else if (verbose > 0) {
    console.log("$" + earliest.toFixed(4) + " to $" + latest.toFixed(4) + ": No good");
  }
};

//Update the trade list every 5 seconds
setInterval(function(){update_trade_list()}, 5000);
//See if a trade should be made every ten seconds
setInterval(function(){check_if_changed(trade_threshold)}, 10000);

//Screw proper error handling
process.on('uncaughtException', function (err) {
  console.log("### API CONNECTION ERROR (1) ###");
  console.log(err);
});
