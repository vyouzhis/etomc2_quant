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
from libs.buildReturnJson import buildReturnJson as brj

def main():

    qm = quantMaKline()
    qm.setmal(20)
    code = None
    brjObject = brj()

    mdfCode = None

    if(len(sys.argv) == 2):
        code = sys.argv[1]

        gc = getAllStock()
        cl = gc.getIndustryCode(code)
        col = ["code", "name","returns"]
        mdfCode = pd.DataFrame(columns=col)
        for c in cl:

            pri = qm.makline(c['code'])
            if pri is None:
                continue
            pdser = pd.Series([c["code"],c['name'], pri],index=col )
            mdfCode = mdfCode.append(pdser,ignore_index=True)

        #print "2"
    elif (len(sys.argv) == 3):
        code = sys.argv[1]

        pri = qm.makline(code)
        print pri
    else:
        print "2"


    mdfCodeMe = mdfCode[mdfCode.code == code].copy()

    if mdfCodeMe.code.count() > 0:
        mdfCodeMe.loc[:,"returns"] = mdfCodeMe["returns"].apply(lambda x: "%.02f%%"%x)
        json = mdfCodeMe.to_json(orient="split")

        brjObject.RawMa(1)
        brjObject.db(json)
        brjObject.formats("table")
        brjObject.name(code)
        brjObject.buildData()

    gmdf = qm.getCodeMa510()
    #gmdf = gmdf.set_index(["code"])
    del gmdf["mas"]
    del gmdf["mal"]

    gmdfCode = gmdf[gmdf.code == code]
    if gmdfCode.code.count()>0:
        json = gmdfCode.sort_values(by="date").to_json(orient="split")

        brjObject.RawMa(1)
        brjObject.db(json)
        brjObject.formats("table")
        brjObject.name(code)
        brjObject.buildData()

    json = gmdf[gmdf["type"] == "buy"].sort_values(by="date").tail(8).to_json(orient="split")

    brjObject.RawMa(1)
    brjObject.db(json)
    brjObject.formats("table")
    brjObject.name("makline buy")
    brjObject.buildData()

    json = gmdf[gmdf["type"] == "sell"].sort_values(by="date").tail(8).to_json(orient="split")

    brjObject.RawMa(1)
    brjObject.db(json)
    brjObject.formats("table")
    brjObject.name("makline buy")
    brjObject.buildData()

    cols = ["right", "loss","right sum", "loss sum", "differ"]
    mdfCodes = pd.DataFrame(columns=cols)

    right = mdfCode[mdfCode.returns > 0].returns.count()
    loss = mdfCode[mdfCode.returns < 0].returns.count()
    right_sum = sum(mdfCode[mdfCode.returns > 0].returns)
    loss_sum = sum(mdfCode[mdfCode.returns < 0].returns)
    mean = "%.02f%%"%(right_sum - abs(loss_sum))
    pdser = pd.Series([right,loss,"%.02f%%"%(right_sum),"%.02f%%"%loss_sum,mean],index=cols)
    mdfCodes = mdfCodes.append(pdser,ignore_index=True)

    json = mdfCodes.to_json(orient="split")

    brjObject.RawMa(1)
    brjObject.db(json)
    brjObject.formats("table")
    brjObject.name("result")
    brjObject.buildData()

    mdfRes = mdfCode.sort_values(by="returns", ascending=False)
    mdfRes.loc[:,"returns"] = mdfRes["returns"].apply(lambda x: "%.02f%%"%x)
    json = mdfRes.to_json(orient="split")

    brjObject.RawMa(1)
    brjObject.db(json)
    brjObject.formats("table")
    brjObject.name("makline")
    brjObject.buildData()

    bjson = brjObject.getResult()
    print bjson

    #print sum(gmdf.returns)
        #print "3"
        #for i in range(1,20):
        #StockTrade(5, 30)

if __name__ == "__main__":
    main()
