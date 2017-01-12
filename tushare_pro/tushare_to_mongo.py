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
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
from emongo import emongo

class TTM():
    def __init__(self):
        self._code = None
        self._Type = None
        self._id = 0
        self._df = None
        self._Init = 0

    def setType(self, t=None):
        self._Type = t

    def setCode(self, c):
        self._code = c

    def setInit(self, i):
        self._Init = i

    def IsExists(self):
        TodayTime = strftime("%Y-%m-%d", localtime(time()))
        emg = emongo()
        sdb = emg.getCollectionNames("stockDB")

        stockName = self._code

        if self._code == 'sh':
#上证指数
            self._code = 'sh000001'
            stockName = "sh"
        elif self._code == 'sz':
#深证指数
            self._code = 'sz399001'
            stockName = "sz"
        elif self._code == 'zx':
#中小板指数
            self._code = 'sz399005'
            stockName = "zx"
        elif self._code == 'cy':
#创业板指数
            self._code = 'sz399006'
            stockName = "cy"
        elif self._code == '300':
#沪深300
            self._code = 'sh000300'
            stockName = "hs300"


        if self._Type is not None:
            stockName = self._code+"_hfq"

        if self._Init == 1:
            emg.remove(stockName)
            return

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

            if df is None:
                return
            if df.empty:
                return

            df = df.reset_index()
            df.date = df["date"].astype(str)
        else:
            #df = ts.get_hist_data(self._code)
            df = self.getSinaKline()

        if df is None:
            return

        if df.empty:
            return
        #print df
        if df.close.count() == 0:
            return

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

    def getSinaKline(self):

        stockNumber = self._code
        if len(stockNumber) == 8:
#8位长度的代码必须以sh或者sz开头，后面6位是数字
            if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
                self._code = stockNumber
        elif len(stockNumber) == 6:
# 6位长度的代码必须全是数字
            if stockNumber.decode().isdigit():
# 0开头自动补sz，6开头补sh，3开头补sz，否则无效
                if stockNumber.startswith('0'):
                    self._code = 'sz' + stockNumber
                elif stockNumber.startswith('6'):
                    self._code = 'sh' + stockNumber
                elif stockNumber.startswith('3'):
                    self._code = 'sz' + stockNumber

        url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=%s&scale=240&datalen=10"%(self._code)
        try:
            request = Request(url)
            text = urlopen(request, timeout=10).read()
            text = text.replace("\"", "")

            text = text.replace(",",",\"")
            text = text.replace(":","\":")
            text = text.replace("{","{\"")

            text = text.replace("day\":","day\":\"")
            text = text.replace(",\"open","\",\"open")

            text = text.replace("},\"{",  "},{")
            djson = json.loads(text)
            df = pd.DataFrame(djson)
            df.rename(columns=lambda x: x.replace('day', 'date'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price5', 'ma5'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price10', 'ma10'), inplace=True)
            df.rename(columns=lambda x: x.replace('ma_price30', 'ma30'), inplace=True)
            #print df
            return df
        except Exception as e:
            print(e)

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
            #ttm.setInit(1)
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

        hs = ["zx","sh","sz","cy","300"]
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
