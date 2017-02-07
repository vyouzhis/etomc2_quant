#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import sys
from emongo import emongo

if(len(sys.argv) == 2):
    stock = sys.argv[1]
    df = ts.get_hist_data(stock,start='2016-08-10', end="2016-08-20")
    JsonList = []
    for i in df.index:
        mydf = df.loc[i]
        mydf["date"] = str(i)
        JsonList.append(mydf.to_dict())

#    print JsonList
    stockDB = {}
    stockDB[stock] = JsonList

    emg = emongo()
    sdb = emg.getCollectionNames("stockDB")

    myDocs = sdb.find_one({stock:{'$exists': True}})

    if myDocs == None:
        sdb.insert(stockDB)
    else:
        udoc = dict(myDocs)
        udoc[stock] = udoc[stock] + JsonList
        val_unique = {v['date']:v for v in udoc[stock]}.values()
        _id = udoc["_id"]
        udoc[stock] = val_unique
        sdb.update({"_id":{"$eq":_id}},{"$set":  udoc })

    emg.Close()
