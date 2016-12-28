#!/usr/bin/python2
# -*- coding: utf-8 -*-
#  trader_quant_atr
#
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#   ATR 线.
#

import sys
import json
import pandas as pd

from libs.kPrice import kPrice
from libs.buildReturnJson import buildReturnJson as brj
from libs.QTaLib import QTaLib

class ATR():
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
        qtl.SetFunName("ATR")
        qtl.SetKline(kline)

        atr = qtl.Run()

        atr = atr[lenhfq-length:]
        o = json.dumps(atr.tolist())

        brjObject = brj()
        brjObject.RawMa(1)

        brjObject.db(o)
        brjObject.formats("line")
        brjObject.name("ATR")
        brjObject.buildData()

        cp = kline.tail(1)

        current_price = cp.close.values[0]
        #获取四天前的收盘价
        prev = kline.tail(5)
        prev = prev.head(1)
        prev_close = prev.close.values[0]
        patr = atr[-1]

        #如果当前价格比之前的价格高一个ATR的涨幅，买入股票
        upside_signal = current_price - (prev_close + patr)
        #如果之前的价格比当前价格高一个ATR的涨幅，卖出股票
        downside_signal = prev_close - (current_price + patr)

        #print upside_signal,"---", downside_signal
        res = []
        order = {}
        order["upside_signal"] = upside_signal
        order["downside_signal"] = downside_signal

        res.append(order)
        df = pd.DataFrame(res)
        jsons = df.to_json(orient="split")
        brjObject.db(jsons)
        brjObject.formats("table")
        brjObject.name("atr")
        brjObject.buildData()

        bjson = brjObject.getResult()
        print bjson


def main(c):
    ks = ATR()
    ks.SetCode(c)
    ks.run()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        code = sys.argv[1]

        main(code)
        #print clist
    else:
        print "2"
