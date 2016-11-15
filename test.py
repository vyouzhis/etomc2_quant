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
year = 2016

month = 1
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
NowTime = "2016-11-01"
endTime = "2016-11-%d"%(calendar.monthrange(2016, 11)[1])
df = ts.get_h_data(stock,start=NowTime, end=endTime)
print df

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
