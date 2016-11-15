#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and un800
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#    该指标是有Richard Donchian发明的，是有3条不同颜色的曲线组成的，
#   该指标用周期（一般都是20）内的最高价和最低价来显示市场价格的波动性，
#   当其通道窄时表示市场波动较小，反之通道宽则表示市场波动比较大
#该具体分析为：
#    当价格冲冲破上轨是就是可能的买的信号；反之，冲破下轨时就是可能的卖的信号。
#    该指标的计算方法为：
#
#    上线=Max（最高低，n）
#    下线=Min（最低价，n）
#    中线=（上线+下线）/2
#

import pymongo
import pandas as pd
import sys

from libs.mongo_data import Feed
from pyalgotrade import bar
from libs.alphaLib import alphaLib as ap
from libs.utils import dataSet

from pyalgotrade import strategy
from pyalgotrade.technical import ma
#from pyalgotrade.utils import dt
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import trades


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, longval=20, shortval=10):
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
            __dateTime = pd.DataFrame()
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

def StockRun(code, lv=20, sv=10):
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code, lv, sv)

    returnsAnalyzer = returns.Returns()

    myStrategy.attachAnalyzer(returnsAnalyzer)

    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    ds = dataSet(myStrategy)
    myStrategy.run()

    rets = ds.getReturns()
    print rets

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        #testAlpha(code)
        StockRun(code)

if __name__ == "__main__":
    main()
