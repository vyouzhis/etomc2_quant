#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb ma5 ma10 kline
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#    当5天均线低于10天均线的时候，买入，反之卖出.
#
import pandas as pd
import sys

from libs.kPrice import getAllStock
from libs.quantMaKline import quantMaKline

def main():

    qm = quantMaKline()
    qm.setmal(20)

    if(len(sys.argv) == 2):
        code = sys.argv[1]

        gc = getAllStock()
        cl = gc.getIndustryCode(code)
        col = ["code","returns", "name"]
        mdf = pd.DataFrame(columns=col)
        for c in cl:

            pri = qm.makline(c['code'])
            if pri is None:
                continue
            pdser = pd.Series([c["code"], pri,c['name']],index=col )
            mdf = mdf.append(pdser,ignore_index=True)
        print mdf.sort_values(by="returns")
        print mdf.returns.mean()
        print "right count:%d, sum:%f"%(mdf[mdf.returns > 0].returns.count(), sum(mdf[mdf.returns > 0].returns))
        print "loss count:%d, sum:%f"%(mdf[mdf.returns < 0].returns.count(), sum(mdf[mdf.returns < 0].returns))

        #print "2"
    elif (len(sys.argv) == 3):
        code = sys.argv[1]

        pri = qm.makline(code)
        print pri
    else:
        print "2"

    gmdf = qm.getCodeMa510()
    gmdf = gmdf.set_index(["code"])

    print gmdf
        #print "3"
        #for i in range(1,20):
        #StockTrade(5, 30)

if __name__ == "__main__":
    main()
