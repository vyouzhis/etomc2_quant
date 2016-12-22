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
        self._col = ["code","format"]
        self._df = pd.DataFrame(columns=self._col)

    def run(self):
        for c in self._clist:
            code = c["code"]
            self.chect(code)

        print self._df

    def chect(self, c):
        kps = kPrice()
        kline = kps.getAllKLine(c+"_hfq")
        if kline is None:
            #print c
            return
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
        t = False
        if mh[0] > 0 and mh[1]>0 and mh[2]>0:
            pdser = pd.Series([c,"ok"],index=self._col)
            self._df = self._df.append(pdser,ignore_index=True)

    def ma(self):
        qm = quantMaKline()
        qm.setmal(20)
        print qm.getSortList()

def main(c):
    macdall = MACDAll(c)
#    macdall.run()
    macdall.ma()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]
        #gas = getAllStock()
        #clist = gas.getIndustryCode(code)
        #clist = gas.getUn800()
        main(code)
        #print clist
    else:
        print "2"
