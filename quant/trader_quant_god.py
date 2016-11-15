#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and un800
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#      黄金分割线的实战运用主要集中在两个方面，一个是利用股价回调和反弹的幅度来预测股价运行趋势，另一个则是判断股价的回调支撑区和反弹压力区。
#

import pymongo
import pandas as pd
import sys
from time import localtime, strftime, time
import datetime
from libs.kPrice import kPrice

def getStockKline(code):

    month = ["01","04","07","10"]
    _mon = strftime("%m", localtime(time()))
    _year = int(strftime("%Y", localtime(time())))
    args = []
    for y in range(_year-1, _year+1):
        for m in month:
            if m == _mon and _year == y:
                break
            a = [y,m]
            args.append(a)
#    col = ["code","god","price","date","nextUP","nextDown","percent"]
    goddf = None

    for m in args[-4:]:
        #print m[0], m[1]
        gdf = runGod(code, m[0], m[1])
        if gdf.code.count() == 0:
            continue

        if goddf is None:
            goddf = gdf
        else:
            goddf =  pd.concat([goddf,gdf])

    if goddf is None:
        return

    if goddf.code.count() > 0:
        print goddf.set_index(["quarter"]).to_json(orient="split")

def runGod(rcode, year, mon):

    godTime = "%s-%s-01"%(year,mon)
    hfqTime = int(datetime.datetime.strptime(godTime, '%Y-%m-%d').strftime("%s"))
    col = ["code","god","price","date","nextUP","nextDown","percent"]
    goddf = pd.DataFrame(columns=col)
    clist = getCode(rcode)

    for c in clist:
        code = str(c['code'])+"_hfq"
        godse = GodStock(code, hfqTime)
        gdf = pd.DataFrame(godse, columns=col)
        gdf["quarter"] = str(year)+str(mon)
        goddf = goddf.append(gdf,ignore_index=True)

    del goddf["god"]
    return goddf
    #if goddf.code.count() > 0:
    #    print goddf.sort_values(by="code").to_json(orient="index")

def getCode(code):

    clist = []
    cl = {}
    cl["code"] = str(code)
    clist.append(cl)
    """
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["AllStockClass"]
    CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
    if CodeIndu.count() == 0:
        return
    clist = None
    for ci in CodeIndu:
        cname = ci['c_name']

        clist = list(sdb.find({"c_name":{"$eq":cname}},{"_id":0,"code":1}))
    """
    return clist

def GodStock(code, hfqTime):
    gs = [0.191,0.382,0.5,0.618,0.809]
    dpress = 0.854
    kp = kPrice()
    kline = kp.getOrderDateKLine(code, hfqTime, 12)
    if kline is None:
        return
    i = 0

    iniClose = 0
    iniDate = ""
    gsInit = 0
    percent = 0
    n = 1
    lp = []
    for k in kline.itertuples():
        if i == 0:
            i+=1
            iniClose = k.close
            iniDate = strftime("%Y-%m-%d", localtime(k.date))
            continue

        if i >= len(gs):
            i=1
            n+=1
            gsInit = gs[i-1]+n
            #gpprice = (gs[i-2]+n)*iniClose
            #percent = ((k.close - gpprice)/ k.close)*100
            #iniClose = k.close
            #iniDate = strftime("%Y-%m-%d", localtime(k.date))

        h = (gs[i-1]+n)*iniClose - k.close
        if h < 0:
            if (i-1)==0 and n == 1:
                lp.append([code,0, iniClose, iniDate,(gs[i-1]+n)*iniClose, iniClose*dpress,0])
            i += 1

            gdate = strftime("%Y-%m-%d", localtime(k.date))
            gsprice = (gs[i-1]+n)*iniClose
            gpprice = (gs[i-2]+n)*iniClose
            percent = ((k.close - gpprice)/ k.close)*100
            lp.append([code,gs[i-1]+n, k.close, gdate,gsprice , k.close*dpress, percent])
#    print lp
    if len(lp) == 0:
        return None
    else:
        return lp

def main():

    if(len(sys.argv) == 2):
        code = sys.argv[1]
        getStockKline(code)
        #print "2"
    else:
        print "3"

if __name__ == "__main__":
    main()
