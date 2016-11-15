#!/usr/bin/python2
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

#from mongo_data import Feed
import pymongo
import pandas as pd

conn = pymongo.MongoClient('127.0.0.1', port=27017)
codeIndex = {}
for szcode in conn.sz50.collection_names():
    if szcode[:2] != "sz":
        continue
    price = conn.sz50[szcode].find_one()['2016-08-03']['close']
    codeInfo = conn.stock['base'].find_one()[szcode[5:]]
    fam = (codeInfo['totals']*10000 * price)*codeInfo['pb']
    fam = "%i"%(fam)
    codeIndex[szcode[5:]] = fam


fampd = pd.DataFrame(codeIndex.items(), columns=['Code', 'fama'], dtype=int)
print(fampd.sort_values(['fama'])[:5])
