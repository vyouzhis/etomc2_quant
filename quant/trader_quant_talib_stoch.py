#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_stoch
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   KDJ 线.
#

import sys
import json

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class KDJ_STOCH():
    def __init__(self):
        self._Code = ""
        self._s = ""

    def SetCode(self, c):
        self._Code = c

    def SetS(self, s):
        self._s = s

    def stoch(self):

        kp = kPrice()
        kline = kp.getAllKLine(self._Code)
        length = len(kline.close.values)
        kline = kp.getAllKLine(self._Code+"_hfq")
        lenhfq = len(kline.close.values)

        qtl = QTaLib()
        qtl.SetFunName(self._s)
        qtl.SetKline(kline)

        slowk, slowd = qtl.Run()

        brjObject = brj()
        brjObject.RawMa(1)

        name1 = "slowk"
        name2 = "slowd"
        if self._s != "STOCH":
            name1 = "fastk"
            name2 = "fastd"

        brjObject.db(json.dumps(slowk[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.name(name1)
        brjObject.buildData()

        brjObject.db(json.dumps(slowd[lenhfq-length:].tolist()))
        brjObject.formats("line")
        brjObject.yIndex(1);
        brjObject.name(name2)
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson

def main(c, m):
    ks = KDJ_STOCH()
    ks.SetCode(c)
    ks.SetS(m)
    ks.stoch()

if __name__ == "__main__":

    if(len(sys.argv) == 3):
        code = sys.argv[2]
        i = sys.argv[1]
        main(code, i)
    else:
        print "2"
