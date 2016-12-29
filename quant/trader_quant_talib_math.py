#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_talib_cycle_indicator
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    cycle_indicator.
#

import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class MATH():
    def __init__(self):
        self._Code = ""
        self._o = ""

    def SetCode(self, c):
        self._Code = c

    def SetO(self, o):
        self._o = o

    def run(self):
        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        length = len(kline.close.values)
        kline = kp.getAllKLine(self._Code+"_hfq")
        lenhfq = len(kline.close.values)

        qtl = QTaLib()
        qtl.SetFunName(self._o)
        qtl.SetKline(kline)

        v1,v2 = qtl.Run()
        brjObject = brj()

        name1 = "min"
        name2 = "max"
        if self._o != "MINMAX":
            name1 = "minidx"
            name2 = "maxidx"

        brjObject.db(json.dumps(v1[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name(name1)
        brjObject.buildData()

        brjObject.db(json.dumps(v2[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.yIndex(1);
        brjObject.name(name2)
        brjObject.buildData()

        brjJson = brjObject.getResult()

        print brjJson


def main(c, o):
    math = MATH()
    math.SetCode(c)
    math.SetO(o)
    math.run()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        code = sys.argv[2]
        o = sys.argv[1]
        main(code, o)
    else:
        print "2"
