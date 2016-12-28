#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_pattern_recognition
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   pr.
#

import talib
from talib import abstract

import sys
import json
import numpy as np

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj

class PR():
    def __init__(self):
        self._Code = ""
        self._i = 0

    def SetCode(self, c):
        self._Code =c

    def SetP(self, i):
        self._i = i

    def run(self):
        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        length = len(kline.close.values)
        kline = kp.getAllKLine(self._Code+"_hfq")
        lenhfq = len(kline.close.values)

        inputs = {
            'open': kline.open.values,
            'high': kline.high.values,
            'low': kline.low.values,
            'close': kline.close.values,
            'volume': kline.volume.values
        }
        res = None

        fun = abstract.Function(self._i)
        res = fun(inputs)
        a = res[0]
        a[np.isnan(a)] = 0
        print a[:20]


def main(c, i):
    pr = PR()
    pr.SetCode(c)
    pr.SetP(i)
    pr.run()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        code = sys.argv[2]
        i = sys.argv[1]
        main(code, i)
    else:
        print "2"
