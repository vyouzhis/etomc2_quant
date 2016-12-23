#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_macd
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   macd 均线.
#


import talib
import sys
import json
import pandas as pd

from libs.kPrice import kPrice
from libs.kPrice import getAllStock
from libs.buildReturnJson import buildReturnJson as brj
from libs.quantMaKline import quantMaKline

class MACDAll():

    def __init__(self, l):
        self._clist = l
        self._col = ["code","mh0","mh1","mh2"]
        self._df = pd.DataFrame(columns=self._col)

    def run(self):
        for c in self._clist:
            code = c["code"]
            self.chect(code)

        print self._df

    def chect(self, c):
        gs = [0.019,0.038,0.05,0.0618,0.0809,0.191,0.382,0.5,0.618,0.809]
        kps = kPrice()
        kline = kps.getAllKLine(c+"_hfq")
        if kline is None:
            #print c
            return
        klast = kline.tail(1)
        k90 = kline.tail(90)
        minClose = k90.sort_values(by="close").head(1)

        print "up:"
        for n in gs:
            print minClose.close.values[0]*(1+n)

        print "down:"
        for m in gs:
            print minClose.close.values[0]*(1-m)

        print klast.close.values[0]

        inputs = {
            'open': kline.open.values,
            'high': kline.high.values,
            'low': kline.low.values,
            'close': kline.close.values,
            'volume': kline.volume.values
        }
        tmacd,macdsing,macdhist = talib.abstract.MACD(inputs)
        length = len(macdhist)
        mh = macdhist[length-3:]
        #print c
        #print mh
        #t = False
        if mh[0] < mh[1] and mh[1] < mh[2] and mh[0]<0:
            pdser = pd.Series([c,mh[0],mh[1],mh[2]],index=self._col)
            self._df = self._df.append(pdser,ignore_index=True)

    def ma(self):
        qm = quantMaKline()
        qm.setmal(20)
        print qm.getSortList()

def main(c):
    macdall = MACDAll(c)
    macdall.run()
#    macdall.ma()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        clist = []
        code = sys.argv[1]
        c = {}
        c["code"] = code
        clist.append(c)
        #gas = getAllStock()
        #clist = gas.getIndustryCode(code)
        #clist = gas.getUn800()

        main(clist)
        #print clist
    else:
        print "2"
