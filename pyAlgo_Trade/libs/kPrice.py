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
import talib

class kPrice():
    def __init__(self):
        self.__conn = pymongo.MongoClient('127.0.0.1', port=27017)
        self.__sdb = self.__conn.etomc2["stockDB"]

    def getAllKLine(self,code):
        """
            获取某一个时间的K 线
        Parameters
        ---------
            code:String 代码
        Return
        -------
            DataFrame
        """
        KL = []
        for post in self.__sdb.find({code: {'$exists':1}},{code:1,'_id':0}):
            KL = post[code]
        if len(KL) == 0:
            return None
        mdf = pd.DataFrame(KL)
        mdf = mdf.sort_values(by="date")
        return mdf

    def talibMa(self, df, tp):
        """
            获得不同的 Moving average
        Parameters
            df:DataFrame  K line
            tp:int  k number
        Return:
            list
        """
        inputs = {
            'open': df.open.values,
            'high': df.high.values,
            'low': df.low.values,
            'close': df.close.values,
            'volume': df.volume.values
        }
        tma = talib.abstract.MA(inputs, timeperiod=tp)
        return tma

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

        mdf = self.getAllKLine(code)

        return mdf.sort_values(by=oby).tail(lmt)

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

    def getInfo(self,ym, ctype, c):
        """
            getInfo 获取 stockinfo 信息
        Parameters
        ---------
            ym:int  年份月份
            ctype:String 类型
            c:String  code
        Return
        -------
            DataFrame

        """
        conn = pymongo.MongoClient('192.168.1.83', port=27017)

        BasicsList = conn.etomc2["stockInfo"].find({"ym":{"$eq":ym}},{"Info."+ctype+"."+c:1,"_id":0, "ym":1}).limit(1)
        if BasicsList.count() != 0:
            bl = BasicsList[0]['Info'][ctype]
            df = pd.DataFrame(data=bl)
            return df.T
        else:
            return None
