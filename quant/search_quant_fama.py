#!/usr/bin/python2
# -*- coding: utf-8 -*-
# quant_fama
#
# use mongodb
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    fama
#   在每个月的最后一个交易日，计算出每个股票的总市值 * 市净率
# 市净率=（P/BV）即：每股市价(P)/每股净资产(Book Value)

import pandas as pd
import sys
from time import localtime, strftime, time

from libs.kPrice import kPrice
from libs.kPrice import getAllStock
from libs.buildReturnJson import buildReturnJson as brj

def runFama(code):
    kp = kPrice()
    st = strftime("%Y-%m-%d", localtime(time()-86400*15))
    cd = code["code"]
    kl = kp.getOrderDateKLine(cd, st, 1)
    if kl is None:
        return None
    lprice =  list(kl.close)[-1]
    ctype = "basics"
    ym = "20162"
    gas = getAllStock()
    basics = gas.getInfo(ym, ctype, cd)
    total =  float(basics.totals) * lprice
    bvps = lprice / float(basics.bvps)
    return total * bvps



def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        gas = getAllStock()
        clist = gas.getIndustryCode(code)
#        col = ['code','fama']
#        sdf = pd.DataFrame(columns=col, dtype=int)
        codeIndex = {}
        fams = []
        codes = []
        names = []
        for cd in clist:
            rf = runFama(cd)
            if rf is None:
                continue
            fam = "%i"%(rf)
            fams.append(fam)
            codes.append(cd["code"])
            names.append(cd["name"])

        codeIndex["fama"] = fams
        codeIndex["code"] = codes
        codeIndex["name"] = names

        fampd = pd.DataFrame(codeIndex, columns=['fama','code','name'])

        if fampd.code.count() > 0:
            fampd.fama = fampd["fama"].astype(int)
#            print fampd.sort_values(by="fama")
            json = fampd.sort_values(by="fama").to_json(orient="split")
#            json = sdf.sort_values(by="收益率").to_json(orient="split")

            brjObject = brj()
            brjObject.db(json)
            brjObject.formats("table")
            brjObject.name("fama")
            brjObject.buildData()
            bjson = brjObject.getResult()
            print bjson

#        print sdf.sort_values(by="fama")
if __name__ == "__main__":
    main()
