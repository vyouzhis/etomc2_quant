#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_macd
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   macd 均线.
#

import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class Macd():
    def __init__(self):
        self._Code = ""
        self._m = ""

    def SetM(self, m):
        self._m = m

    def getCode(self, c):
        self._Code = c

        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        length = len(kline.close.values)
        kline = kp.getAllKLine(self._Code+"_hfq")
        lenhfq = len(kline.close.values)

        qtl = QTaLib()
        qtl.SetFunName(self._m)
        qtl.SetKline(kline)

        res = qtl.Run()

        tmacd,macdsing,macdhist = res

        brjObject = brj()
        brjObject.RawMa(1)

        brjObject.db(json.dumps(tmacd[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name(self._m)
        brjObject.buildData()

        brjObject.db(json.dumps(macdsing[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name("signal Line")
        brjObject.buildData()

        brjObject.db(json.dumps(macdhist[lenhfq-length:].tolist()))
        brjObject.formats("bar")
        brjObject.yIndex(1);
        brjObject.name("MACD-Histogram")
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson


def main(c, m):
    macd = Macd()
    macd.SetM(m)
    macd.getCode(c)

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        code = sys.argv[2]
        i = sys.argv[1]
        main(code, i)
    else:
        print "2"
