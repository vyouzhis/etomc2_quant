#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_obv
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   obv.
#

import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class RSI():
    def __init__(self):
        self._Code = ""

    def SetCode(self, c):
        self._Code = c

    def run(self):
        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        length = len(kline.close.values)
        kline = kp.getAllKLine(self._Code+"_hfq")
        lenhfq = len(kline.close.values)

        qtl = QTaLib()
        qtl.SetFunName("RSI")
        qtl.SetKline(kline)

        rsiReal= qtl.Run()

        brjObject = brj()

        brjObject.db(json.dumps(rsiReal[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name("RSI")
        brjObject.buildData()

        brjJson = brjObject.getResult()
        print brjJson

def main(c):
    rsi = RSI()
    rsi.SetCode(c)
    rsi.run()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]
        main(code)
    else:
        print "2"
