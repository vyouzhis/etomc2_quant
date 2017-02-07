#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import sys

stock = []
if(len(sys.argv) > 1):
    for i in range(1,len(sys.argv)):
        stock.append(sys.argv[i])
else:

    stock.append("sh")
    stock.append("sz")
    stock.append("hs300")
    stock.append("sz50")

df = ts.get_realtime_quotes(stock)
JsonList = []
for i in df.index:
    mydf = df.loc[i]
    mydf["date"] = str(i)
    JsonList.append(mydf.to_dict())

print JsonList
"""
    stockDB = {}
    stockDB[stock] = JsonList
    myDocs = conn.etomc2["stockDB"].find_one({stock:{'$exists': True}})

    if myDocs == None:
        conn.etomc2["stockDB"].insert(stockDB)
    else:
        udoc = dict(myDocs)
        udoc[stock] = udoc[stock] + JsonList
        val_unique = {v['date']:v for v in udoc[stock]}.values()
        _id = udoc["_id"]
        udoc[stock] = val_unique
        conn.etomc2["stockDB"].update({"_id":{"$eq":_id}},
                                                            {"$set":  udoc })
                                                            """
