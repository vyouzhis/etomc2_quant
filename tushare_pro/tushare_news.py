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
from emongo import emongo

df = ts.get_latest_news(top=50,show_content=True)
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
        newTalk[post['code']] = nadf.to_dict(orient="list")

print newTalk
#print json.dumps(newTalk)
