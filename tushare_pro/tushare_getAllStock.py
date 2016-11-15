#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import pymongo
import tushare as ts
conn = pymongo.MongoClient('192.168.1.83', port=27017)
df = ts.get_industry_classified()

JsonList = []
for i in df.index:
    JsonList.append(df.loc[i].to_dict())

conn.etomc2["AllStockClass"].insert(JsonList)
