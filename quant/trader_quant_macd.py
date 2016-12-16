#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb ma5 ma10 kline
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#    当5天均线低于10天均线的时候，买入，反之卖出.
#

import talib
import pandas as pd
import sys
import json

from libs.kPrice import getAllStock
from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj

class Macd():
    def __init__(self):
        self._Code = ""

    def getCode(self, c):
        self._Code = c
        kps = kPrice()
        kline = kps.getAllKLine(c)
        inputs = {
            'open': kline.open.values,
            'high': kline.high.values,
            'low': kline.low.values,
            'close': kline.close.values,
            'volume': kline.volume.values
        }
        tmacd,macdsing,macdhist = talib.abstract.MACD(inputs)

        brjObject = brj()
        brjObject.RawMa(0)

        brjObject.db(json.dumps(tmacd.tolist()))
        brjObject.formats("line")
        brjObject.name("macd")
        brjObject.buildData()

        brjObject.db(json.dumps(macdsing.tolist()))
        brjObject.formats("line")
        brjObject.name("signal Line")
        brjObject.buildData()

        brjObject.db(json.dumps(macdhist.tolist()))
        brjObject.formats("bar")
        brjObject.name("MACD-Histogram")
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson


def main(c):
    macd = Macd()
    macd.getCode(c)

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]
        main(code)
    else:
        print "2"
