#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    pe search stock
#

import pymongo
import pandas as pd
import sys
from time import localtime, strftime, time
import datetime

def getInfo(ym, ctype, c):
    conn = pymongo.MongoClient('192.168.1.83', port=27017)

    BasicsList = conn.etomc2["stockInfo"].find({"ym":{"$eq":ym}},{"Info."+ctype+"."+c:1,"_id":0, "ym":1}).limit(1)
    if BasicsList.count() != 0:
        bl = BasicsList[0]['Info'][ctype]
        df = pd.DataFrame(data=bl)
        return df.T
    else:
        return None

def getKLine(code, st):
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["stockDB"]
    ma20 = sdb.find({code+".date":{"$gte":st}},{"_id":0}).sort(code+".date", pymongo.ASCENDING).limit(1)

    if ma20.count() == 0:
        #print "code:%s is None"%(code)
        return None
    mdf = pd.DataFrame(ma20[0][code])
    mdf = mdf.sort_values(by="date")
    return mdf


def test():
    codes="601988"
    ty = "basics"
    ym1 = "20141"
    s = getInfo(ym1, ty, codes)
    #print s
    ost = s.outstanding[codes]

    ty = "profit"
    month = 0
    year_month = ""
    eyear_month = ""
    for y in range(2014,2017):
        for m in range(1,5):
            if y == 2016 and m == 3:
                break
            yms = str(y)+str(m)
            si = getInfo(yms, ty, codes)
            if si.empty:
                continue
#                print si.net_profits
            ceps = si.eps[codes]
            cnet_profits = si.net_profits[codes]

            month = m*3;
            year_month = str(y)+"-"+str(month)+"-01"
            eyear_month = str(y)+"-"+str(month)+"-31"
            if month < 10:
                year_month = str(y)+"-0"+str(month)+"-01"
                eyear_month = str(y)+"-0"+str(month)+"-31"

#            t = int(datetime.datetime.strptime(year_month, '%Y-%m-%d').strftime("%s"))
            kl = getKLine(codes, year_month)
#            print kl
#            kl.date = kl.date.apply(lambda x:strftime("%Y-%m-%d", localtime(x)))
#            step = kl.date.count()
            #ceps = cnet_profits/ost
            kl.close = kl[kl.date<=eyear_month].close.apply(lambda x:(x/ceps))

            print yms
            print kl

def getPrice(code):
    st = strftime("%Y-%m-%d", localtime(time()-86400*5))
    k = getKLine(code,st)
    if k is None:
        return None
    return k.close[1:2][1]

def testeps(codes):
    ty = "profit"
    ym1 = "20152"
    s = getInfo(ym1, ty, codes)
    net_profits = s.net_profits[codes]

    ym1 = "20154"
    s = getInfo(ym1, ty, codes)
    net_profits = s.net_profits[codes] - net_profits

    ym1 = "20162"
    s = getInfo(ym1, ty, codes)
    if s is None:
        return 0
    if ("net_profits" in s) == False:
        return 0
    net_profits += s.net_profits[codes]

    cprice = getPrice(codes)
    if cprice is None:
        #print "price is 0"
        return 0
    ty = "basics"
    inf = getInfo(ym1, ty, codes)
    top = inf.totals[codes]*cprice/ 100
    return top/net_profits

def getIndustry(code):
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["AllStockClass"]
    CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
    if CodeIndu.count() == 0:
        return

    col = ["name","code","pe"]
    pedf = pd.DataFrame(columns=col)
    for ci in CodeIndu:
        cname = ci['c_name']

        Indu = sdb.find({"c_name":{"$eq":cname}},{"_id":0})
        for pecode in Indu:
            pcode = pecode["code"]
            pe = testeps(pcode)
            if pe <= 0:
                continue
            pdser = pd.Series([pecode["name"], pcode, pe],index=col )
            #print pdser
            pedf = pedf.append(pdser,ignore_index=True)
            #print "name:%s, code:%s, pe:%02f"%(pecode["name"], pcode, pe)
    #print pedf.to_json(orient="split")
    print pedf.sort_values(by="pe").to_json(orient="split")
    #me = pedf.pe.mean()
    #print "pe mean:",me
    #print "lt:",pedf[pedf.pe < me].pe.count()
    #print "gt:",pedf[pedf.pe > me].pe.count()
    #print pedf[pedf.code == code].pe

def main():
    ym1 = "20131"
    ym2 = "20162"
    st = "2016-01-01"
    col = ['code','pe','pb','md201','md202', 'mdsum']
    pepd = pd.DataFrame(columns=col)

    if(len(sys.argv) == 2):
        #code = "600808"
        code = sys.argv[1]
        #testeps(code)
        getIndustry(code)
        #print "2"
    else:
        bdf1 = getInfo(ym1)
        bdf1 = bdf1.sort_values(by="pe")
        bdf1 = bdf1[bdf1.pe > 0]
        for code in bdf1.index:

            pe = bdf1.pe[code]
            pb = bdf1.pb[code]
            kl = getKLine(code, st)
            if kl is None:
                continue
            ma201 = kl.ma20[kl.index[0]]
            ma202 = kl.ma20[kl.index[-1]]
#            print "%s, %s, %s, %s"%(pe1, pe2, ma201, ma202)
            s = pd.Series([code,pe,pb,ma201,ma202, (ma202-ma201)], index=col)
            pepd  = pepd.append(s, ignore_index=True)
        pe15 = pepd[pepd.pe <= 15]
        print "pe15  mdsum:%.2f"%(pe15.mdsum.mean())

        pe20 = pepd[pepd.pe > 15]
        pe20 = pe20[pe20.pe <= 20]
        print "pe20  mdsum:%.2f"%(pe20.mdsum.mean())

        pe60 = pepd[pepd.pe > 20]
        pe60 = pe60[pe60.pe <= 60]
        print "pe60  mdsum:%.2f"%(pe60.mdsum.mean())
        pe70 = pepd[pepd.pe > 60]
        print "pe70  mdsum:%.2f"%(pe70.mdsum.mean())

if __name__ == "__main__":
    main()
