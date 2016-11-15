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

import time
import pymongo

class MySQLDatabase(dbfeed.Database):
    def getBars(self, instrument, timezone=None, fromDateTime=None, toDateTime=None):
        conn = pymongo.MongoClient('127.0.0.1', port=27017)
        szCode = conn.etomc2[instrument]
        ret = []
        for post in szCode.find():
            for key, val in post.items():
                if key == '_id':
                    continue
                dateTime = key
                TimeStamp = time.mktime(time.strptime(dateTime,'%Y-%m-%d'))
                OdateTime = dt.timestamp_to_datetime(TimeStamp)
#                print("%s"%dateTimes)
                ret.append(bar.BasicBar(OdateTime, val['open'], val['high'], val['low'], val['close'], val['volume'], val['close'], bar.Frequency.DAY))

        return ret


class Feed(membf.BarFeed):
    def __init__(self, instrument, frequency, maxLen=None):
        super(Feed, self).__init__(frequency, maxLen)
        self.__instrument = instrument
        self.__mySQLdb = MySQLDatabase()

    def barsHaveAdjClose(self):
        return True

    def getDatabase(self):
        return self.__mySQLdb

    def loadBars(self, timezone=None, fromDateTime=None, toDateTime=None):
        bars = self.__mySQLdb.getBars(self.__instrument,timezone, fromDateTime, toDateTime)
        self.addBarsFromSequence(self.__instrument, bars)
