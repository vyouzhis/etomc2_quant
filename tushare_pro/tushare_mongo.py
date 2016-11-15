#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import pymongo
import sys,json
import tushare as ts
from time import localtime, strftime, time
import pandas as pd
import calendar

class pyMongodb():
    def __init__(self):
        self.__code = None
        self.__stockType = None
        self.__df = None
        self.__year = 2015
        self.__month = 9
        self.__day = ""
        self.__id = ""

    def setCode(self, code):
        self.__stockType = None
        self.__code = code

    def setType(self, Type):
        self.__stockType = Type

    def setDay(self, day):
        self.__day = day

    def setYear(self, year):
        self.__year = year

    def runKLine(self):

#        t = int(datetime.datetime.strptime('2016-09-01', '%Y-%m-%d').strftime("%s"))
#        myDocs = conn.etomc2["stockDB"].find({"600808_hfq.date":{"$gte": t}}, {"_id":0,"600808_hfq.date":1}).sort("600808_hfq.date", pymongo.ASCENDING)
#        print list(myDocs)
#        NowTime = strftime("%Y-%m-%d", localtime(time()-86400))
#        endTime = None
        #NowTime = strftime("%Y-%m-%d", localtime(time()))

        conn = pymongo.MongoClient('192.168.1.83', port=27017)
        sdb = conn.etomc2["stockDB"]
        stockName = self.__code
        if self.__stockType is not None:
            stockName = self.__code+"_hfq"
        isExists = sdb.find({stockName:{"$exists":1}},{stockName:1, "_id":1}).sort(stockName+".date", pymongo.DESCENDING).limit(1)
        for ie in isExists:
            self.__df = pd.DataFrame(ie[stockName])
            self.__id = ie['_id']
        exis = isExists.count()
        conn.close()

        if exis == 0:
            self.initKLine(self.__year, 1)
        else:
            StartTime = str(list(self.__df.date)[-1])
            if len(StartTime) > 0:
                year = int(StartTime[0:4])
                mon = int(StartTime[5:7])
                #print "year:%s, mon:%s"%(year,mon)
                self.initKLine(year, mon)
            else:
                self.initKLine(self.__year, 1)

    def initKLine(self, syear, smon):
        day = self.__day
        NowYM = int(strftime("%Y%m", localtime(time())))
        endYear = int(strftime("%Y", localtime(time())))+1
        mformat = "%d-0%d-%s"
        bformat = "%d-%d-%s"

        for y in range(syear, endYear):
            for m in range(smon, 13):

                StartTime = "%d-0%d-01"%(y, m)
                if len(self.__day) == 0 :
                    day = str(calendar.monthrange(y, m)[1])
                endTime = mformat%(y, m, day)

                if m > 9:
                    StartTime = "%d-%d-01"%(y, m)
                    endTime = bformat%(y, m, day)

                #print "%s now:%s ,end: %s"%(self.__code, StartTime, endTime)
                if int(str(y)+str(m)) > NowYM:
                    #print "end time ",StartTime
                    return
                self.SaveKLine(StartTime, endTime)
                #return

    def SaveKLine(self, NowTime, endTime):
        conn = pymongo.MongoClient('192.168.1.83', port=27017)

        df = None
        if self.__stockType == None:
            df = ts.get_hist_data(self.__code,start=NowTime, end=endTime)
        else:
            df = ts.get_h_data(self.__code, autype=self.__stockType, start=NowTime, end=endTime)

        if df is None:
            #print "df is none",NowTime, endTime
            return

        df = df.reset_index()
        df = df.sort_values(by="date")
        if df.date.count() == 0:
            return
        kDays = list(df.date)[0]
        flag = True
 #       print str(kDays)

        if self.__df is not None:
            sDays = list(self.__df.date)[0]
#            print str(sDays)
            if str(kDays)[0:7] == str(sDays)[0:7]:
                df = self.__df.append(df)
#lambda x:strftime("%Y-%m-%d", localtime(x))
                k = df.drop_duplicates(subset=['date'], keep=False)
                df = self.__df.append(k, ignore_index=True)
                flag = False

        cjson = df.to_json(orient="records", date_format="epoch",date_unit="s")
        j = json.loads(cjson)

        stockDB = {}

        stockName = self.__code
        if self.__stockType is not None:
            stockName = self.__code+"_hfq"
        print stockName
        stockDB[stockName] = j
        if flag:
            conn.etomc2["stockDB"].insert(stockDB)
        else:
            conn.etomc2["stockDB"].update({"_id":{"$eq":self.__id}},
                                                                {"$set":  stockDB })
        conn.close()

class getAllStock():
    def getas(self):
        pmdb = pyMongodb()
        conn = pymongo.MongoClient('192.168.1.83', port=27017)
        szCode = conn.etomc2["AllStockClass"]
        codeList = list(szCode.find({},{"code":1,"_id":0}))
        conn.close()

        for post in codeList:
            code = post["code"]
            print code
            pmdb.setCode(code)

            pmdb.setType(None)
            pmdb.runKLine()

            pmdb.setType("hfq")
            pmdb.runKLine()

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        pmdb = pyMongodb()
        pmdb.setCode(code)
        print "get one stock:",code
        if code == "hs300":
#            pmdb.setDay("09")
            pmdb.runKLine()
            return
        conn = pymongo.MongoClient('192.168.1.83', port=27017)
        sdb = conn.etomc2["AllStockClass"]
        CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
        if CodeIndu.count() == 0:
            return

        for ci in CodeIndu:
            cname = ci['c_name']

            Indu = sdb.find({"c_name":{"$eq":cname}},{"_id":0})
            for pecode in Indu:
                pcode = pecode["code"]
                pmdb.setCode(pcode)
                pmdb.runKLine()
                pmdb.setType("hfq")
                pmdb.runKLine()
    else:
        print "get all stock"
        gas = getAllStock()
        gas.getas()


if __name__ == "__main__":
    main()
