#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

from pyalgotrade import strategy
from pyalgotrade import bar
from pyalgotrade.technical import ma
#from pyalgotrade.utils import dt
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import trades

from pandas import DataFrame
import numpy as np
import pandas as pd

from mongo_data import Feed
from mongo_data import MonSQLDatabase
import utils
import sys
import json

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, longval=21, shortval=3):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.setDebugMode(False)
        self.__instrument = instrument
        self.__feed = feed

        self.ds = feed.getDataSeries(instrument).getCloseDataSeries()
        self.__smaLong = ma.SMA(self.ds, longval)
        self.__smaShort = ma.SMA(self.ds, shortval)

        self.__prices = feed[instrument].getPriceDataSeries()
        self.__position = None
        self.__profit = 0
        self.__buy = 0
        self.__sell = 0
        self.__buys=[]
        self.__sells=[]

    def getSells(self):
        return self.__sells

    def getBuys(self):
        return self.__buys

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f" % (execInfo.getPrice()))
        buy_price={}
        buy_price["time"]=execInfo.getDateTime().strftime('%Y-%m-%d')
        buy_price["price"]=execInfo.getPrice()
        self.__buys.append(buy_price)

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        #self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None
        sell_price={}
        sell_price["time"]=execInfo.getDateTime().strftime('%Y-%m-%d')
        sell_price["price"]=execInfo.getPrice()
        self.__sells.append(sell_price)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def getsmaLong(self):
        return self.__smaLong

    def getsmaShort(self):
        return self.__smaShort

    def getProfit(self):
        return self.__profit

    def getDateTimeSeries(self,instrument=None):
        if instrument is None:
            __dateTime = DataFrame()
#            for element in self.__instrument:
            __dateTime = __dateTime.append(self.__feed[self.__instrument].getPriceDataSeries().getDateTimes())
            __dateTime = __dateTime.drop_duplicates([0])
            #print(__dateTime.values.__len__())
            return __dateTime.values #此时返回的为二维数组
        return self.__feed[instrument].getCloseDataSeries().getDateTimes()

    def onBars(self, bars):
        if self.__smaLong[-1] == None:
            return

        #bar = bars[self.__instrument]

        if self.__position is None:
            if cross.cross_above(self.__prices, self.__smaLong) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__prices, self.__smaLong) > 0:
            self.__position.exitMarket()

    def getRet(self):
        return "good"

def Alpha(rts):
    mongo = MonSQLDatabase()

    mongo.getBars("hs300")
#    rts = mongo.getData(code)
    rbts = mongo.getDF()

    dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                                                'b_adjclose' : rbts['Adj Close']},
                                                index=rts.index)

# compute returns
    dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
            dfsm[['s_adjclose','b_adjclose']].shift(1) -1
    dfsm = dfsm.dropna()
    covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])

# calculate measures now
    beta = covmat[0,1]/covmat[1,1]
    alpha= np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])

# r_squared     = 1. - SS_res/SS_tot
    ypred = alpha + beta * dfsm["b_returns"]
    SS_res = np.sum(np.power(ypred-dfsm["s_returns"],2))
    SS_tot = covmat[0,0]*(len(dfsm)-1) # SS_tot is sample_variance*(n-1)
    r_squared = 1. - SS_res/SS_tot
# 5- year volatiity and 1-year momentum
    volatility = np.sqrt(covmat[0,0])
    momentum = np.prod(1+dfsm["s_returns"].tail(12).values) -1

# annualize the numbers
    prd = 12. # used monthly returns; 12 periods to annualize
    alpha = alpha*prd
    volatility = volatility*np.sqrt(prd)
    alphas={}
    alphas["beta"] = "%.3f"%(beta)
    alphas["alpha"] = "%.3f"%(alpha*100)
    alphas["r_squared"] = r_squared
    alphas["volatility"] = volatility
    alphas["momentum"] = momentum
    return alphas

def StockRun(code, lv=21, sv=3):
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()
    Json = {}

    if (code != "hs300"):
        Json['alpha'] = Alpha(dbfeed.getDF())

    myStrategy = MyStrategy(dbfeed, code, lv, sv)

    returnsAnalyzer = returns.Returns()

    myStrategy.attachAnalyzer(returnsAnalyzer)

    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    ds = utils.dataSet(myStrategy)

    myStrategy.run()

    #print ds.getSharpeRatio()
    #print ds.getCumulativeReturns()
    #print json.dumps(ds.getReturns())

    Json['returns'] = ds.getReturns()
    Json['sharpe'] = "%.3f" % (ds.getSharpeRatio())
    Json['maxDraw'] = "%.3f"%(ds.getMaxDrawDown()*100)
    Json['buy'] = myStrategy.getBuys()
    Json['sell'] = myStrategy.getSells()
    Json['profit'] = "%.3f" % (returnsAnalyzer.getCumulativeReturns()[-1] * 100)

    print  json.dumps(Json)
#    return myStrategy.getProfit()

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
def main():

    if(len(sys.argv) == 2):
        code = sys.argv[1]
#    print "code:",code
        StockRun(code)
    else:
        print "code is not"

if __name__ == "__main__":
    main()
