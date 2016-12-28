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

    def getCode(self, c):
        self._Code = c
        kps = kPrice()
        kline = kps.getAllKLine(c)
        qtl = QTaLib()
        qtl.SetFunName("MACD")
        qtl.SetKline(kline)

        res = qtl.Run()

        tmacd,macdsing,macdhist = res

        brjObject = brj()
        brjObject.RawMa(1)

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
        brjObject.yIndex(1);
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
