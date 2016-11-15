#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import pymongo
import json
import pandas as pd
from time import localtime, strftime, time


conn = pymongo.MongoClient('192.168.1.83', port=27017)
szCode = conn.etomc2["stockInfo"]
ym = "20151"
wh = "profit"
whfild = "bips"
whcode = wh+".code"

codeList = list(szCode.find({ym:{"$exists":1}},{"_id":0, ym+"."+wh+"."+whfild:1,whcode:1}))
lst = codeList[0][ym][wh]

s = pd.DataFrame(lst)
goodCode = s.sort_values(by=whfild,ascending=False)
#goodCode = goodCode[str(goodCode['cashflowratio']) != "NaN"]
goodCode = goodCode.dropna(how="any")

BasicsList = list(szCode.find({ym:{"exists":1}},{"_id":0, ym+".basics":1}))
BL = pd.DataFrame(BasicsList[0][0]['basics'])
ordby = "timeToMarket"
BLa = BL.T[BL.T[ordby] < 20150101]

BLa = BLa[BLa[ordby] > 0]

#ordby = "industry"
BLc = BLa.sort_values(by=ordby).index

BLo = goodCode[goodCode.code.isin(BLc)]

length = BLo.code.count()

sdb = conn.etomc2["stockDB"]

step = 0
offset = 0
nt = int(round(length/6))
np = nt
ct = 0
m = 0
hfq = ""
#print BLo
goodCT = []
badCT = []
for i in BLo.index:
    whf = "%.2f"%BLo[whfild][i]

    k = BLo.code[i]

    val = sdb.find({k+hfq:{"$exists":1}},{k+hfq+".ma20":1,k+hfq+".date":1,"_id":0})
    lval = list(val)
    if len(lval) < 1:
#        print k," is null"
        continue
    cp = lval[0][k+hfq]
    if cp[-1]["date"] != "2016-09-29 00:00:00":
        continue
    cplen = len(cp)

    if cplen < (step+1):
#        print k," is 360"
        continue

    print "stime:%s, etime:%s"%(cp[step]["date"], cp[-1]["date"])
    startPrice = cp[step]["ma20"]
    endPrice = cp[-1]["ma20"]

    if offset > np:
        np+=nt
        print "sum:%f"%(ct)
        ct = 0
        m=0
    offset+=1
    m+=1

    ct += float(endPrice) - float(startPrice)
"""
    if ct > 0:
        g = {}
        g[whf] = "%.2f"%ct
        goodCT.append(g)
    else:
        b = {}
        b[whf] = "%.2f"%ct
        badCT.append(b)
#    print "whfile:%s  ct:%f"%(whf, ct)
#print goodCT
#print "--"
#print badCT
"""
