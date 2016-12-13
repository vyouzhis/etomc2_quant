#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
#  斐波那契数列
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    pe search stock
#

import pymongo
import pandas as pd
import sys

from libs.mongo_data import Feed
from pyalgotrade import bar
from libs.alphaLib import alphaLib as ap
from libs.utils import dataSet
from libs.buildReturnJson import buildReturnJson as brj

from pyalgotrade import strategy
from pyalgotrade.technical import ma
#from pyalgotrade.utils import dt
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import trades


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

def StockRun(code, lv=21, sv=3):
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code, lv, sv)

    returnsAnalyzer = returns.Returns()

    myStrategy.attachAnalyzer(returnsAnalyzer)

    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)

    ds = dataSet(myStrategy)
    myStrategy.run()

#    Json['returns'] = ds.getReturns()
    rets = ds.getReturns()
    return sum(list(pd.DataFrame(rets).item.apply(lambda x :float(x))))
#    print "%s" % (returnsAnalyzer.getCumulativeReturns())

 #   print  json.dumps(Json)

def testAlpha(code):
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    alpha = ap()

    cdf = alpha.Alpha(dbfeed.getDF())
    print cdf

def getIndustry(code):
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["AllStockClass"]
    CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
    if CodeIndu.count() == 0:
        return
    codes = []
    for ci in CodeIndu:
        cname = ci['c_name']

        Indu = sdb.find({"c_name":{"$eq":cname}},{"_id":0})
        for pecode in Indu:
            codes.append(pecode["code"])
    return codes

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        #testAlpha(code)
        #clist = getIndustry(code)
        clist = []
        clist.append(code)
        col = ['code','长均线','短均线','收益率']
        sdf = pd.DataFrame(columns=col)
        slist = [1,2,3,5,8,13,21,34]
        llist = [2,3,5,8,13,21,34,55,89,144]
        for cd in clist:

            for m in range(1,len(slist)):
                s = slist[m]
                l = llist[m+1]
                sr = StockRun(cd, l, s)
                ps = pd.Series([cd, l,s, sr],index=col)
                sdf = sdf.append(ps,ignore_index=True)

        json = sdf.sort_values(by="收益率").to_json(orient="split")

        brjObject = brj()
        brjObject.RawMa(1)
        brjObject.db(json)
        brjObject.formats("table")
        brjObject.name("fiboseq")
        brjObject.buildData()
        bjson = brjObject.getResult()
        print bjson
#        print sdf.groupby(['lv','sv']).mean().sort_values(by="returns")

if __name__ == "__main__":
    main()
