#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_bbands
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   BBANDS 线.
#

import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class BBANDS():
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
        qtl.SetFunName("BBANDS")
        qtl.SetKline(kline)

        upperband, middleband, lowerband = qtl.Run()

        brjObject = brj()
        brjObject.RawMa(0)

        brjObject.db(json.dumps(upperband[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.isExt(1)
        brjObject.yIndex(1)
        brjObject.name("Upper Band")
        brjObject.buildData()

        brjObject.db(json.dumps(middleband[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.isExt(1)
        brjObject.yIndex(1)
        brjObject.name("5-day SMA")
        brjObject.buildData()

        brjObject.db(json.dumps(lowerband[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.isExt(1)
        brjObject.yIndex(1)
        brjObject.name("Lower Band")
        brjObject.buildData()

        brjJson = brjObject.getResult()

        print brjJson

def main(c):
    bb = BBANDS()
    bb.SetCode(c)
    bb.run()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]

        main(code)
        #print clist
    else:
        print "2"
