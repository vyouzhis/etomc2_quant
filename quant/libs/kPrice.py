#!/usr/bin/python2
# -*- coding: utf-8 -*-
# kPrice
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#     获取股票的基本信息，包括K线，代码等
#
import pymongo
import pandas as pd

class kPrice():
    def __init__(self):
        self.__conn = pymongo.MongoClient('192.168.1.83', port=27017)
        self.__sdb = self.__conn.etomc2["stockDB"]

    def getAllKLine(self,code):

        KL = []
        for post in self.__sdb.find({code: {'$exists':1}},{code:1,'_id':0}):
            KL = KL+post[code]
        if len(KL) == 0:
            return None
        mdf = pd.DataFrame(KL)
        mdf = mdf.sort_values(by="date")
        return mdf

    def getOrderDateKLine(self, code, oby, lmt):
        """
            获取某一个时间的K 线
        Parameters
        ---------
            code:String 代码
            oby:date 时间
            lmt:int 数量
        Return
        -------
            DataFrame
        """
        KL = []
        for post in self.__sdb.find({code+".date":{"$gte":oby}},{"_id":0}).sort(code+".date", pymongo.ASCENDING).limit(lmt):
            KL = KL+post[code]
        if len(KL) == 0:
            return None
        mdf = pd.DataFrame(KL)
        mdf = mdf.sort_values(by="date")
        return mdf

    def HS300Time(self,nextTime = None):
        """
            以HS300Time 为标准时间
        Parameters
        ---------
            nextTime:date  开始时间值
        Return
        -------
            Series
        """
        kl = kPrice()
        hs300 = kl.getAllKLine("hs300")
        hs300 = hs300.sort_values(by="date")
        if nextTime is None:
            return hs300.date
        else:
            return hs300[hs300.date >= nextTime].date

class getAllStock():
    def getUn800(self):
        """
            获取上证 800 股票
        Parameters
        ---------
        Return
        -------
            list
        """
        conn = pymongo.MongoClient('192.168.1.83', port=27017)
        szCode = conn.etomc2["un800"]
        codeList = list(szCode.find({},{"code":1,"_id":0}))
        conn.close()

        return codeList

    def getIndustryCode(self, code):
        """
            获取该股票的行业代码
        Parameters
        ---------
        code:string  代码
        Return
        -------
            list
        """
        conn = pymongo.MongoClient('192.168.1.83', port=27017)
        sdb = conn.etomc2["AllStockClass"]
        CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
        if CodeIndu.count() == 0:
            return
        clist = None
        for ci in CodeIndu:
            cname = ci['c_name']

            clist = list(sdb.find({"c_name":{"$eq":cname}},{"_id":0,"code":1,"name":1}))

        return clist
