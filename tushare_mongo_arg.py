#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import pymongo
import json
import tushare as ts
import sys

conn = pymongo.MongoClient('192.168.1.83', port=27017)
#stock="hs300"
if(len(sys.argv) == 2):
	stock = sys.argv[1]
    df = ts.get_hist_data(stock,start='2016-01-01')
    print df.index
"""
    JsonList = []
    for i in df.index:
        mydf = df.loc[i]
        mydf["date"] = str(i)
        JsonList.append(mydf.to_dict())

    stockDB = {}
    stockDB[stock] = JsonList
    myDocs = conn.etomc2["stockDB"].find_one({stockName:{'$exists': True}})

    if myDocs == None:
        conn.etomc2["stockDB"].insert(stockDB)
    else:
        udoc = dict(myDocs)
        udoc[stockName] = udoc[stockName] + JsonList
        val_unique = {v['date']:v for v in udoc[stockName]}.values()
        newlist = sorted(val_unique, key=lambda k: k['date'], reverse=False)

        _id = udoc["_id"]
        udoc[stockName] = newlist

#            print newlist

        conn.etomc2["stockDB"].update({"_id":{"$eq":_id}},
"""                                                                {"$set":  udoc })
#    print JsonData
	#conn.etomc2[stock].insert(JsonData)
