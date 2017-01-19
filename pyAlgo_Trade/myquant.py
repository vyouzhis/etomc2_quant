#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  home
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#  测试　pyalgotrade 回测
#

from libs.MongoStock import Feed

from pyalgotrade import bar
from pyalgotrade import strategy
from pyalgotrade import technical

import sys

class SMAEventWindow(technical.EventWindow):
    def __init__(self, period):
        assert(period > 0)
        super(SMAEventWindow, self).__init__(period)
        self.__value = None

    def onNewValue(self, dateTime, value):
        firstValue = None
        if len(self.getValues()) > 0:
            firstValue = self.getValues()[0]
            assert(firstValue is not None)

        super(SMAEventWindow, self).onNewValue(dateTime, value)

        if value is not None and self.windowFull():
            if self.__value is None:
                self.__value = self.getValues().mean()
            else:
                self.__value = self.__value + value / float(self.getWindowSize()) - firstValue / float(self.getWindowSize())

    def getValue(self):
        return self.__value


class SMA(technical.EventBasedFilter):

    def __init__(self, dataSeries, period, maxLen=None):
        super(SMA, self).__init__(dataSeries, SMAEventWindow(period), maxLen)


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__sma = SMA(feed[instrument].getCloseDataSeries(), 15, 1024)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
#        self.info(self.__sma)
        self.info("price:%s, sma:%s, date:%s"%(bar.getPrice() , self.__sma[-1], bar.getDateTime()))

def main(code):
    #code = "000592"
    dbfeed = Feed(code, bar.Frequency.DAY, 1024)
    dbfeed.loadBars()

    myStrategy = MyStrategy(dbfeed, code)
    myStrategy.run()

if __name__ == "__main__":
    code = sys.argv[1]
    main(code)
