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
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import trades
from pyalgotrade.utils import stats
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import trades

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
        #print self.__msdf.returns.sum()

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        #self.info("BUY at $%.2f"%(execInfo.getPrice()))
        self.__buyPrice = execInfo.getPrice()
        self.__buyTime = execInfo.getDateTime()

    def onEnterCanceled(self, position):
        #self.info("onEnterCanceled")
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

        if shares == 0 and bar.getClose() < lower:
            sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
            self.__position = self.enterLong(self.__instrument, sharesToBuy, False)
        elif shares > 0 and bar.getClose() > upper:
            self.__position.exitMarket()


def main(i, code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code, bBandsPeriod=i)

    retAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    drawDownAnalyzer = drawdown.DrawDown()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
    myStrategy.attachAnalyzer(drawDownAnalyzer)

    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    myStrategy.run()

#交易过程
    myStrategy.EchoDF()

#总资产
    print "Final portfolio value: $%.2f" % myStrategy.getResult()
#累计收益率
    print "Anual return: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100)
#    平均收益率
    print "Average daily return: %.2f %%" % (stats.mean(retAnalyzer.getReturns()) * 100)
#方差收益率
    print "Std. dev. daily return: %.4f" % (stats.stddev(retAnalyzer.getReturns()))
#夏普比率
    print "Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0))
#最大回撤
    print "DrawDown : %.2f" % (drawDownAnalyzer.getMaxDrawDown())

    print "++++++++++"
#总交易笔数
    print("Total trades: %d" % (tradesAnalyzer.getCount()))
    if tradesAnalyzer.getCount() > 0:
        profits = tradesAnalyzer.getAll()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Profits std. dev.: $%2.f" % (profits.std()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))
        returns_trade = tradesAnalyzer.getAllReturns()
        print("Avg. return: %2.f %%" % (returns_trade.mean() * 100))
        print("Returns std. dev.: %2.f %%" % (returns_trade.std() * 100))
        print("Max. return: %2.f %%" % (returns_trade.max() * 100))
        print("Min. return: %2.f %%" % (returns_trade.min() * 100))

#盈利笔数
    print("------")
    print("Profitable trades: %d" % (tradesAnalyzer.getProfitableCount()))
    if tradesAnalyzer.getProfitableCount() > 0:
        profits = tradesAnalyzer.getProfits()
        print("Avg. profit: $%2.f" % (profits.mean()))
        print("Profits std. dev.: $%2.f" % (profits.std()))
        print("Max. profit: $%2.f" % (profits.max()))
        print("Min. profit: $%2.f" % (profits.min()))
        returns_trade = tradesAnalyzer.getPositiveReturns()
        print("Avg. return: %2.f %%" % (returns_trade.mean() * 100))
        print("Returns std. dev.: %2.f %%" % (returns_trade.std() * 100))
        print("Max. return: %2.f %%" % (returns_trade.max() * 100))
        print("Min. return: %2.f %%" % (returns_trade.min() * 100))

#亏损笔数
    print("=============")
    print("Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount()))
    if tradesAnalyzer.getUnprofitableCount() > 0:
        losses = tradesAnalyzer.getLosses()
        print("Avg. loss: $%2.f" % (losses.mean()))
        print("Losses std. dev.: $%2.f" % (losses.std()))
        print("Max. loss: $%2.f" % (losses.min()))
        print("Min. loss: $%2.f" % (losses.max()))
        returns_trade = tradesAnalyzer.getNegativeReturns()
        print("Avg. return: %2.f %%" % (returns_trade.mean() * 100))
        print("Returns std. dev.: %2.f %%" % (returns_trade.std() * 100))
        print("Max. return: %2.f %%" % (returns_trade.max() * 100))
        print("Min. return: %2.f %%" % (returns_trade.min() * 100))


if __name__ == "__main__":
    code = sys.argv[1]
    #for m in range(10,60,5):
    m = 40
    main(m, code)
