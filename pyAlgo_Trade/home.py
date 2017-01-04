#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  home
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#  测试　pyalgotrade 回测
#
from libs.MongoStock import MonSQLDatabase
from libs.MongoStock import Feed

from pyalgotrade import strategy
from pyalgotrade import bar
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
#from pyalgotrade.utils import dt
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.utils import stats
from pyalgotrade.technical import bollinger

from pandas import DataFrame
import numpy as np
import pandas as pd

import sys
import json

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, bBandsPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.setDebugMode(False)
        self.__instrument = instrument
        self.__feed = feed
        self.__position = None
#        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)
        #self.__rsi = rsi.RSI(feed[instrument].getCloseDataSeries(), 15)
        #self.__sma = ma.SMA(self.__rsi, 15)
#        print self.__sma
#        bBandsPeriod = 5
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(),
                                                 bBandsPeriod, 2)

        self.__col = ["buyPrice","buyTime","sellPrice","sellTime", "returns"]
        self.__msdf = pd.DataFrame(columns=self.__col)
        self.__buyPrice = 0
        self.__buyTime = None
        self.setUseAdjustedValues(True)

    def EchoDF(self):
        print self.__msdf.tail(30)
        print self.__msdf.returns.sum()

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f"%(execInfo.getPrice()))
        self.__buyPrice = execInfo.getPrice()
        self.__buyTime = execInfo.getDateTime()

    def onEnterCanceled(self, position):
        self.info("onEnterCanceled")
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        #self.info("SELL at $%.2f"%(execInfo.getPrice()))
        self.__position = None

        pdser = pd.Series([self.__buyPrice, self.__buyTime,
                           execInfo.getPrice(),execInfo.getDateTime(), (execInfo.getPrice() -self.__buyPrice)],index=self.__col )
        self.__msdf = self.__msdf.append(pdser,ignore_index=True)
        self.__buyPrice = 0
        self.__buyTime = None

    def onExitCanceled(self, position):
        self.info("onExitCanceled")
        self.__position.exitMarket()

    def marketOrder(self, instrument, quantity, onClose=False, goodTillCanceled=False, allOrNone=False):
        self.info("%s  %s"%(instrument, quantity))

    def getFilled(self):
        print self.getBroker().getPositions()

    def onBars(self, bars):
        """
        if self.__sma[-1] is None:
            return
        bar = bars[self.__instrument]
        #self.info("close:%s sma:%s rsi:%s" % (bar.getClose(), self.__sma[-1], self.__rsi[-1]))

        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
                #print dir(self.__position)

        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()

        """

        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)

        bar = bars[self.__instrument]

        print("close %s  %s %s" % (bar.getClose(), bar.getAdjClose(), bar.getDateTime()))

        if shares == 0 and bar.getClose() < lower:
            sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
            self.marketOrder(self.__instrument, sharesToBuy)
            self.__position = self.enterLong(self.__instrument, sharesToBuy, False)
        elif shares > 0 and bar.getClose() > upper:
            self.marketOrder(self.__instrument, -1*shares)
            self.__position.exitMarket()


def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code, bBandsPeriod=i)

    retAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)


    myStrategy.run()
    #print(("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()))
    #print "Final portfolio value: $%.2f" % myStrategy.getResult()
    myStrategy.EchoDF()
    myStrategy.getFilled()

    print "Final portfolio value: $%.2f" % myStrategy.getResult()
    print "Anual return: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100)
    print "Average daily return: %.2f %%" % (stats.mean(retAnalyzer.getReturns()) * 100)
    print "Std. dev. daily return: %.4f" % (stats.stddev(retAnalyzer.getReturns()))
    print "Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0))


if __name__ == "__main__":
    #for m in range(5,60,5):
    m = 40
    print m
    code = sys.argv[1]
    main(m, code)
