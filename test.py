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
from time import localtime, strftime, time
import calendar
import pandas as pd
import numpy as np
import talib
import stockstats

"""
df = ts.get_latest_news()
ndf = df[~(df.url.str.match(".*jsy", as_indexer=True))]

contTime = strftime("%m-%d %H:%M", localtime(time()-3660))

ndf = df[df.time > contTime]

conn = pymongo.MongoClient('192.168.1.83', port=27017)
szCode = conn.etomc2["AllStockClass"]
codeList = list(szCode.find({},{"_id":0, "name":1,"code":1}))

newTalk = {}
for post in codeList:
    name = post['name'].replace("*", "").strip()
    re_name = ".*"+name
    nadf = ndf[ndf.title.str.match(re_name, as_indexer=True)]
    if len(nadf):
        newTalk[post['code']] = nadf.to_dict()

print json.dumps(newTalk)
"""
#year = 2016

#month = 1
#cashflowDf = ts.get_cashflow_data(year,month)

def toJson(dfData):
    index = dfData.set_index(["code"]).index
    dfData.index = index
    cl = dfData.drop_duplicates("code")
    cl.pop("code")
    cjson = cl.to_json(orient="index")
    j = json.loads(cjson)
    return j

#print toJson(cashflowDf)
#print code_cashflowDf.head(2).drop_duplicates("code")
#j = json.loads(code_cashflowDf.to_json(orient="index"))
#print j
stock = "601988"
NowTime = "2016-01-01"
endTime = "2016-11-%d"%(calendar.monthrange(2016, 11)[1])
#df = ts.get_h_data(stock,start=NowTime, end=endTime)
df = ts.get_h_data(stock, autype="hfq", start=NowTime, end=endTime)
#df = df.reset_index()
#df.date = df["date"].astype(str)
#print df
#stock = stockstats.StockDataFrame.retype(df)
#print stock.get("macd")
#print "----------"
inputs = {
    'open': df.open.values,
    'high': df.high.values,
    'low': df.low.values,
    'close': df.close.values,
    'volume': df.volume.values
}

#print inputs
#tma = talib.abstract.MA(df.close.values, timeperiod=5)
#print tma
tmacd,macdsing,macdhist = talib.abstract.MACD(inputs)
print tmacd
print "--------"
print macdsing
print "============="
print macdhist
#df["ma5"] = tma
#print df
#cjson = df.to_json(orient="records", date_format="epoch",date_unit="s")
#j = json.loads(cjson)
#print j

#df = ts.get_notices(stock)
#nurl = df.url[26]
#cont = ts.notice_content(nurl)
#print ts.forecast_data(year=2016,quarter=1)
#nav = ts.get_nav_grading("all")
#print nae[]
#ba = ts.get_stock_basics()
#ts.get_cashflow_data
#ba.rename(columns=lambda x: x.replace('esp', 'eps'), inplace=True)
#print ba.columns


def pdIndex():
    s = 1
    a = [1,2,3]
    if s == 1:
        a = [1,3,2]
    elif s == 2:
        a = [2,3,1]
    elif s == 3:
        a = [2,1,3]
    elif s == 4:
        a = [3,1,2]
    elif s == 5:
        a = [3,2,1]

    print a
    df1 = pd.DataFrame({'A':a},index=np.arange(1,4,1))
    df1 = df1.sort_values(by="A")
    print df1.index

    df2 = pd.DataFrame({'A':[1,3,2]},index=np.arange(1,4,1))
    df2 = df2.sort_values(by="A")
    print df2.index

    print df2.index.equals(df1.index)

    print np.arange(1,4, 1)
#pdIndex()

def KDJ(date,N=9,M1=3,M2=3):
    datelen=len(date)
    array=np.array(date)
    kdjarr=[]
    for i in range(datelen):
        if i-N<0:
            b=0
        else:
            b=i-N+1
        rsvarr=array[b:i+1,0:5]
        rsv=(float(rsvarr[-1,-1])-float(min(rsvarr[:,3])))/(float(max(rsvarr[:,2]))-float(min(rsvarr[:,3])))*100
        if i==0:
            k=rsv
            d=rsv
        else:
            k=1/float(M1)*rsv+(float(M1)-1)/M1*float(kdjarr[-1][2])
            d=1/float(M2)*k+(float(M2)-1)/M2*float(kdjarr[-1][3])
        j=3*k-2*d
        kdjarr.append(list((rsvarr[-1,0],rsv,k,d,j)))
    return kdjarr
