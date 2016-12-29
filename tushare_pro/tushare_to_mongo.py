#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  tushare_to_mongo
#
#
# vim:fileencoding=utf-8:sw=4:et
#
#   从tushare获取Ｋ线数据
#

import sys,json
import pandas as pd
import tushare as ts
from time import localtime, strftime, time
import pymongo
import multiprocessing

from emongo import emongo

class TTM():
    def __init__(self):
        self._code = None
        self._Type = None
        self._id = 0
        self._df = None

    def setType(self, t=None):
        self._Type = t

    def setCode(self, c):
        self._code = c

    def IsExists(self):
        TodayTime = strftime("%Y-%m-%d", localtime(time()))
        emg = emongo()
        sdb = emg.getCollectionNames("stockDB")

        stockName = self._code
        if self._Type is not None:
            stockName = self._code+"_hfq"

        isExists = sdb.find({stockName:{"$exists":1}},{stockName:1, "_id":1}).limit(1)
        for ie in isExists:
            self._df = pd.DataFrame(ie[stockName])
            self._id = ie['_id']
        exis = isExists.count()
        if exis != 0:
            tdf = self._df.tail(1)
            sdate =  tdf.date.values[0]
            if sdate == TodayTime:
                print "ok date, ",TodayTime
                return

        if self._Type is not None:
            stime = self.getBaseDate(exis)
            if stime is None:
                return

            df = ts.get_h_data(self._code, autype=self._Type, start=stime)
        else:
            df = ts.get_hist_data(self._code)

        if df is None:
            return

        if df.close.count() == 0:
            return

        df = df.reset_index()
        df.date = df["date"].astype(str)

        stockDB = {}

        if exis == 0:
            cjson = df.sort_values(by="date").to_json(orient="records")
            j = json.loads(cjson)

            stockDB[stockName] = j
            sdb.insert(stockDB)
        else:
            self._df = self._df.append(df.head(20))
            self._df = self._df.drop_duplicates()
            cjson = self._df.sort_values(by="date").to_json(orient="records")
            j = json.loads(cjson)
            stockDB[stockName] = j

            sdb.update({"_id":{"$eq":self._id}}, {"$set":  stockDB })

        emg.Close()

    def getBaseDate(self, m):
        StartTime = strftime("%Y-%m-%d", localtime(time()-86400*5))
        if m == 1:
            return StartTime

        emg = emongo()
        sdb = emg.getCollectionNames("stockInfo")
        df = sdb.find({"Info.basics."+self._code:{"$exists":1}},{"Info.basics."+self._code+".timeToMarket":1,"_id":0}).sort("ym", pymongo.DESCENDING).limit(1)

        baseTime = None
        for i in df:
            baseTime = str(i["Info"]["basics"][self._code]["timeToMarket"])
            break

        if baseTime is None:
            return None

        emg.Close()
        baseTime = baseTime[0:4]+"-"+baseTime[4:6]+"-"+baseTime[6:]

        return baseTime


class getAllStock():
    def getas(self, t=None):

        emg = emongo()
        cname = "AllStockClass"
#        cname = "un800"
        szCode = emg.getCollectionNames(cname)
        codeList = list(szCode.find({},{"code":1,"_id":0}))
        emg.Close()
        print t, " is start"
        i = 0
        for post in codeList:
            code = post["code"]

            ttm = TTM()
            ttm.setCode(code)
            ttm.setType(t)
            ttm.IsExists()
            print "now next is:",i
            i+=1

        print t," is end"


def runStock(types=None):
    gas = getAllStock()
    gas.getas(types)

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        hs = ["hs300","sh","sz","sz50"]
        if code in hs:
            ttm = TTM()
            ttm.setCode(code)
            ttm.IsExists()
            return
        gas = getAllStock()
        gas.getas()
    else:
        print "get all stock"
        try:
            h = multiprocessing.Process(target = runStock, args = ("hfq",))
            h.start()
            n = multiprocessing.Process(target = runStock, args = ())
            n.start()
        except:
            print "Error: unable to start thread"
        print "end"


if __name__ == "__main__":
    main()
