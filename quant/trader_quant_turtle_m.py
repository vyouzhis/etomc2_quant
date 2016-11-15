#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and un800
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#    该指标是有Richard Donchian发明的，是有3条不同颜色的曲线组成的，
#   该指标用周期（一般都是20）内的最高价和最低价来显示市场价格的波动性，
#   当其通道窄时表示市场波动较小，反之通道宽则表示市场波动比较大
#该具体分析为：
#    当价格冲冲破上轨是就是可能的买的信号；反之，冲破下轨时就是可能的卖的信号。
#    该指标的计算方法为：
#
#    上线=Max（最高低，n）
#    下线=Min（最低价，n）
#    中线=（上线+下线）/2
#
from libs.kPrice import kPrice
import sys

def turtle(code):
    kl = kPrice()
    kdb = kl.getAllKLine(code)
    preClose = 0
    dayHigh = []
    dayLog = []
    dayAve = []
    for k in kdb.itertuples():
        if preClose == 0:
            preClose = k.close
            continue

        m = max(k.high-k.low, k.high - preClose, preClose - k.low)
        n = min(k.high-k.low, k.high - preClose, preClose - k.low)
        ma = {}
        mi = {}
        if len(dayHigh) > 19:
            mv = [d[d.keys()[0]] for d in ma]
            m = (sum(mv[-19:])+m)/20
            nv = [d[d.keys()[0]] for d in mi]
            n = (sum(nv[-19:])+m)/20

        ma[k.date] = "%02f"%m
        dayHigh.append(ma)
        mi[k.date] = "%02f"%n
        dayLog.append(mi)
        dv = {}
        dv[k.date] = "%02f"%((m+n)/2)
        dayAve.append(dv)

    dh = dayHigh[13:]
    print [d[d.keys()[0]] for d in dh]
    dl = dayLog[13:]
    print [d[d.keys()[0]] for d in dl]
    da = dayAve[13:]
    print [d[d.keys()[0]] for d in da]
#        print "date:%s  hight:%02f, low:%02f, close:%02f "%(k.date, k.high,k.low,k.close)

def main():

    if(len(sys.argv) == 2):
        code = sys.argv[1]
        turtle(code)
        print "2"
    else:
        print "3"

if __name__ == "__main__":
    main()
