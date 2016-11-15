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

import pymongo
import pandas as pd
import sys
from time import localtime, strftime, time

def getKLine(code, st):
    """
        获取K 线数据
    Parameters
    ---------
    code:string 代码
    st:date 开始的时间
    Return
    -------
    DataFrame

    """
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["stockDB"]
    price = sdb.find({code+".date":{"$gte":st}},{"_id":0}).sort(code+".date", pymongo.ASCENDING).limit(1)

    if price.count() == 0:
        #print "code:%s is None"%(code)
        return None
    mdf = pd.DataFrame(price[0][code])
    mdf = mdf.sort_values(by="date")
    return mdf

def getInfo(ym, ctype, c):
    """
        获取K 线数据
    Parameters
    ---------
    code:string 代码
    st:date 开始的时间
    Return
    -------
    DataFrame

    """
    conn = pymongo.MongoClient('192.168.1.83', port=27017)

    BasicsList = conn.etomc2["stockInfo"].find({"ym":{"$eq":ym}},{"Info."+ctype+"."+c:1,"_id":0, "ym":1}).limit(1)
    if BasicsList.count() != 0:
        bl = BasicsList[0]['Info'][ctype]
        df = pd.DataFrame(data=bl)
        return df.T
    else:
        return None

def runFama(code):
    st = strftime("%Y-%m-%d", localtime(time()-86400*5))
    kl = getKLine(code, st)
    if kl is None:
        return None
    lprice =  list(kl.close)[-1]
    ctype = "basics"
    ym = "20162"
    basics = getInfo(ym, ctype, code)
    total =  float(basics.totals) * lprice
    bvps = lprice / float(basics.bvps)
    return total * bvps

def getIndustry(code):
    conn = pymongo.MongoClient('192.168.1.83', port=27017)
    sdb = conn.etomc2["AllStockClass"]
    CodeIndu = sdb.find({"code":{"$eq":code}},{"_id":0}).limit(1)
    if CodeIndu.count() == 0:
        return
    codes = []
    for ci in CodeIndu:
        cname = ci['c_name']

        Indu = sdb.find({"c_name":{"$eq":cname}},{"_id":0})
        for pecode in Indu:
            codes.append(pecode["code"])
    return codes

def main():
    if len(sys.argv) == 2:
        code = sys.argv[1]
        clist = getIndustry(code)
#        col = ['code','fama']
#        sdf = pd.DataFrame(columns=col, dtype=int)
        codeIndex = {}
        for cd in clist:
            rf = runFama(cd)
            if rf is None:
                continue
            fam = "%i"%(rf)
            codeIndex[str(cd)] = fam
        fampd = pd.DataFrame(codeIndex.items(), columns=['Code', 'fama'], dtype=int)
        if fampd.Code.count() > 0:
            print(fampd.sort_values(by="fama").to_json(orient="split"))
#        print sdf.sort_values(by="fama")
if __name__ == "__main__":
    main()
