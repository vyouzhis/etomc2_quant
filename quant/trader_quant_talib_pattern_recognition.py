#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_pattern_recognition
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   pr.
#

import sys
import json
import numpy as np

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

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

        qtl = QTaLib()
        qtl.SetFunName(self._i)
        qtl.SetKline(kline)

        tpr = qtl.Run()

        tpr = tpr[lenhfq-length:]
        brjObject = brj()
        brjObject.RawMa(1)

        brjObject.db(json.dumps(tpr.tolist()))
        brjObject.formats("bar")
        brjObject.name(self._i)
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson

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
