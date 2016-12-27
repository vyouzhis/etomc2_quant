#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_stoch
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   KDJ 线.
#

import talib
import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj

class KDJ_STOCH():
    def __init__(self):
        self._Code = ""

    def SetCode(self, c):
        self._Code = c

    def stoch(self):
        kp = kPrice()
        kline = kp.getAllKLine(self._Code)

        inputs = {
            'open': kline.open.values,
            'high': kline.high.values,
            'low': kline.low.values,
            'close': kline.close.values,
            'volume': kline.volume.values
        }
        slowk, slowd = talib.abstract.STOCH(inputs, 5, 3, 0, 3, 0)

        brjObject = brj()
        brjObject.RawMa(1)

        brjObject.db(json.dumps(slowk.tolist()))
        brjObject.formats("line")
        brjObject.name("slowk")
        brjObject.buildData()

        brjObject.db(json.dumps(slowd.tolist()))
        brjObject.formats("line")
        brjObject.yIndex(1);
        brjObject.name("slowd")
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson

def main(c):
    ks = KDJ_STOCH()
    ks.SetCode(c)
    ks.stoch()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]

        main(code)
        #print clist
    else:
        print "2"
