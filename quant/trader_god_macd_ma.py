#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_god_macd_ma
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   当　５天均线　从下往上穿过20天均线并且　macd
#   的histogram　慢慢往上时候可以买入
#   以　20 天均线的最低值作为
#   macd ma 均线 god
#

import talib
import sys
import json
import pandas as pd

from libs.kPrice import kPrice
from libs.kPrice import getAllStock
from libs.buildReturnJson import buildReturnJson as brj
from libs.quantMaKline import quantMaKline

class GodMACDMA():
    def __init__(self):
        self._CurrentCode = ""
        self._CodeList = []
        self._HFQKline = None
        self._Kline = None
        self._MACDHistogram = []

        self._md50 = []
        self._md20 = []
        self._BuyFlag = False

        self._GodValInit = 0

        self._col = ["code","date", "close","hfqclose", "returns","type"]
        self._Returns = pd.DataFrame(columns=self._col)

    def SetCodeList(self, l):
        self._CodeList = l

    def GodListener(self):
        godBaseList = [0.019,0.038,0.05,0.0618,0.0809,0.191,0.382,0.5,0.618,0.809]

    def macdLister(self):

        inputs = {
            'open': self._HFQKline.open.values,
            'high': self._HFQKline.high.values,
            'low': self._HFQKline.low.values,
            'close': self._HFQKline.close.values,
            'volume': self._HFQKline.volume.values
        }
        tmacd,macdsing,macdhist = talib.abstract.MACD(inputs)
        self._MACDHistogram = macdhist

    def MAListener(self):
        ma5 = 1

    def Loop(self):
        lenHFQ = len(self._HFQKline.open.values)
        lenK = len(self._Kline.open.values)

        self._MACDHistogram = self._MACDHistogram[lenHFQ - lenK : ]

        i = 0

        for row in self._Kline.itertuples():
            i+=1
            #self.SellAction(row, i)
            f = self.BuyAction(row, i)
            if f == 0:
                self.GodValueInit(row)

            if f == -1 and self._BuyFlag:
                self.SellAction(row);

        print self._Returns

    def BuyAction(self, row, i):
        if self._BuyFlag == True:
            return -1

        if len(self._md50) == 3:
            self._md50.pop(0)
        self._md50.append(row.ma5)

        if len(self._md20) == 3:
            self._md20.pop(0)
        self._md20.append(row.ma20)

        maFlag = False
        if len(self._md50) == 3:
            if self._md50[0] <   self._md20[0] and self._md50[2] > self._md20[2]:
                maFlag = True

        if maFlag:
            mh = self._MACDHistogram[i-3:i]
            if mh[2]>mh[1] and mh[1]>mh[0]:

                hclose = self._HFQKline[self._HFQKline.date == row.date].close.values[0]
                pdser = pd.Series([self._CurrentCode, row.date,row.close,hclose,
                                    "0", "buy"],index=self._col)
                self._Returns = self._Returns.append(pdser,ignore_index=True)
                self._BuyFlag = True
                self._GodValInit = 0
                return 0
            else:
                print "no:",row.date

        return 1

    def GodValueInit(self, row):
        k90 = self._HFQKline[self._HFQKline.date <= row.date]
        k90 = k90.tail(90)
        minClose = k90.sort_values(by="close").head(1)
        self._GodValInit = minClose.close.values[0]

    def SellAction(self,row):
        hline = self._HFQKline[self._HFQKline.date == row.date]
        gs = (hline.close - self._GodValInit)/row.close * 100
        print hline.close.values[0]
#        print "rclose:%s, mclose:%s gs:%s date:%s"%(hline.close.values[0], self._GodValInit, gs, row.date)
        #if row.close > minClose.close:
        #    print "s"
        #else:
        #    print "s"


    def GetKLine(self, c):
        kps = kPrice()
        self._HFQKline = kps.getAllKLine(c+"_hfq")
        if self._HFQKline is None:
            print c
            return
        self._Kline = kps.getAllKLine(c)
        if self._Kline is None:
            print c
            return

    def run(self):
        for c in self._CodeList:
            self._CurrentCode = c["code"]
            self.GetKLine(c["code"])
            self.macdLister()
            self.Loop()

def main(c):
    macdall = GodMACDMA()
    macdall.SetCodeList(c)
    macdall.run()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        clist = []
        code = sys.argv[1]
        print code
        c = {}
        c["code"] = code
        clist.append(c)
        main(clist)

    else:
        print "un800"
        gas = getAllStock()
        #clist = gas.getIndustryCode(code)
        clist = gas.getUn800()

        main(clist)
