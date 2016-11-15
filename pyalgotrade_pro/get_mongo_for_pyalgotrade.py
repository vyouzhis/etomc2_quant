#!/usr/bin/python2
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-


from pyalgotrade import strategy
#from pyalgotrade.barfeed import yahoofeed
from pyalgotrade import bar
from pyalgotrade.technical import ma
#from pyalgotrade.utils import dt
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import cross
from pyalgotrade.technical import rsi

from mongo_data import Feed
import pymongo
import pandas as pd

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, longval=21, shortval=3):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
#        self.__rsi = rsi.RSI(feed[instrument].getCloseDataSeries(), 5)
#        self.__smaLong = ma.SMA(self.__rsi, longval)
#        self.__smaShort = ma.SMA(self.__rsi, shortval)
        self.__smaLong = ma.SMA(feed[instrument].getCloseDataSeries(), 21)
        self.__smaShort = ma.SMA(feed[instrument].getCloseDataSeries(), 3)

        self.smarsi = rsi.RSI(feed[instrument].getPriceDataSeries(), 21)

        self.__position = None
        self.__profit = 0
        self.__buy = 0
        self.__sell = 0

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        #self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def getsmaLong(self):
        return self.__smaLong

    def getsmaShort(self):
        return self.__smaShort

    def getProfit(self):
        return self.__profit

    def onBars(self, bars):
        if self.__smaLong[-1] == None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        #self.info("price:%.2f  smaLog:%.2f  smaShort:%.2f" % (bar.getPrice(), self.__smaLong[-1], self.__smaShort[-1]))
        if self.__position is None:
            if cross.cross_above(self.__smaShort, self.__smaLong) > 0:
            #if bar.getPrice() < self.smarsi[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
                self.__buy = bar.getPrice()
        # Check if we have to exit the position.
        elif cross.cross_below(self.__smaShort, self.__smaLong) > 0 and not self.__position.exitActive():
        #elif bar.getPrice() > self.smarsi[-1] and not self.__position.exitActive():
            self.__position.exitMarket()
            self.__sell = bar.getPrice()
            #self.info("-1 short: %.2f long: %.2f "%(self.__smaShort[-1], self.__smaLong[-1]))
            #self.info("-2 short: %.2f long: %.2f "%(self.__smaShort[-2], self.__smaLong[-2]))
            #self.info(" price: %.2f - %.2f"%(self.__buy, self.__sell))
            self.__profit = self.__sell - self.__buy + self.__profit
            self.__buy = 0
            self.__sell = 0

    def getRet(self):
        return "good"

# Load the yahoo feed from the CSV file
#feed = yahoofeed.Feed()
#feed.addBarsFromCSV("orcl", "orcl-2000.csv")


def StockRun(code, lv=21, sv=3):
#print(code+":")
    dbfeed = Feed(code, bar.Frequency.DAY, 10)
    dbfeed.loadBars()
# Evaluate the strategy with the feed's bars.
    myStrategy = MyStrategy(dbfeed, code, lv, sv)


    returnsAnalyzer = returns.Returns()

    myStrategy.attachAnalyzer(returnsAnalyzer)

# Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot(code).addDataSeries("SMALong", myStrategy.getsmaLong())
    plt.getInstrumentSubplot(code).addDataSeries("SMAShort", myStrategy.getsmaShort())

# Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

# Run the strategy.
    myStrategy.run()
    #print(myStrategy.getProfit())
    #ls = {}
    #ls['long'] = list(myStrategy.getsmaLong())
    #ls['short'] = list(myStrategy.getsmaShort())
    #pdls = pd.DataFrame(ls)
    #print(pdls)
    #plt.plot()
    return myStrategy.getProfit()


#    return myStrategy.getProfit()
#res = myStrategy.getRet()
#print(res)
# Plot the strategy.


def orderList():
    conn = pymongo.MongoClient('127.0.0.1', port=27017)
    codeIndex = {}
    for szcode in conn.sz50.collection_names():
        if szcode[:2] != "sz":
            continue
        prof = StockRun(szcode[5:], 89, 8)
        codeIndex[szcode[5:]] = float("{0:.2f}".format(prof))

    pdprofit = pd.DataFrame(codeIndex.items(), columns=['Code', 'Profit'], dtype=float)
    pdprofit = pdprofit.sort_values(['Profit','Code'])
    pdOrder = pdprofit.groupby(['Profit'])
    print(pdOrder.sum())


#code = "600893"
#StockRun(code)

orderList()
