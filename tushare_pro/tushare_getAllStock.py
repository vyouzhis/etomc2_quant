#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

from emongo import emongo
import tushare as ts
df = ts.get_industry_classified()

JsonList = []
for i in df.index:
    JsonList.append(df.loc[i].to_dict())

emg = emongo()
sdb = emg.getCollectionNames("AllStockClass")

sdb.insert(JsonList)
emg.Close()
