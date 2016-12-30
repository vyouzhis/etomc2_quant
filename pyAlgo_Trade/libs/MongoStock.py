#!/usr/bin/python2
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

from pyalgotrade.barfeed import dbfeed
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade.utils import dt

import pandas as pd

import time
from emongo import emongo

class MonSQLDatabase(dbfeed.Database):
    def __init__(self):
        self.__df = None

    def getBars(self, instrument, timezone=None, fromDateTime=None, toDateTime=None):
        emg = emongo()
        stockdb = emg.getCollectionNames("stockDB")
        ret = []
        code = instrument+"_hfq"
        for post in stockdb.find({code: {'$exists':1}},{code:1,'_id':0}):
            Date = []
            Open = []
            High = []
            Low = []
            Close = []
            Volume = []
            Adj_Close = []

            for v in post.items():
                for val in v[1][-500:]:
                    dateTime = val['date']
                    TimeStamp = time.mktime(time.strptime(dateTime,'%Y-%m-%d'))
                    OdateTime = dt.timestamp_to_datetime(TimeStamp)

                    ret.append(bar.BasicBar(OdateTime, val['open'], val['high'], val['low'], val['close'], val['volume'], val['close'], bar.Frequency.DAY))

                    Date.append(TimeStamp)
                    Open.append(val['open'])
                    High.append(val['high'])
                    Low.append(val['low'])
                    Close.append(val['close'])
                    Volume.append(val['volume'])
                    Adj_Close.append(val['close'])

            self.__df = pd.DataFrame({'Date' : Date, 'Open' : Open,
                    'High' : High,'Close' : Close,
                    'Low' : Low,'Volume' : Volume,
                    'Adj Close':Adj_Close})

        return ret

    def getDF(self):
        return self.__df


class Feed(membf.BarFeed):
    def __init__(self, instrument, frequency, maxLen=None):
        super(Feed, self).__init__(frequency, maxLen)
        self.__instrument = instrument
        self.__monSQLdb = MonSQLDatabase()

    def barsHaveAdjClose(self):
        return True

    def getDatabase(self):
        return self.__monSQLdb

    def getDF(self):
        return self.__monSQLdb.getDF()

    def loadBars(self, timezone=None, fromDateTime=None, toDateTime=None):
        bars = self.__monSQLdb.getBars(self.__instrument,timezone, fromDateTime, toDateTime)
        self.addBarsFromSequence(self.__instrument, bars)
