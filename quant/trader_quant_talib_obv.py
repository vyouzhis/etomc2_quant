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


class OBV():
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
        volume = kline.volume.values

        qtl = QTaLib()
        qtl.SetFunName(self._o)
        qtl.SetKline(kline)

        obvReal = qtl.Run()

        brjObject = brj()

        brjObject.db(json.dumps(obvReal[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name(self._o)
        brjObject.buildData()

        brjObject.db(json.dumps(volume[lenhfq-length:].tolist()))
        brjObject.formats("bar")
        brjObject.yIndex(1)
        brjObject.name("Volume")
        brjObject.buildData()
        brjJson = brjObject.getResult()

        print brjJson


def main(c, o):
    obv = OBV()
    obv.SetCode(c)
    obv.SetO(o)
    obv.run()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        code = sys.argv[2]
        o = sys.argv[1]
        main(code, o)
    else:
        print "2"
