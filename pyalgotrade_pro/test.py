#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

#import tushare as ts
#df = ts.get_stock_basics()
#print df


#df3 = ts.get_h_data('002337') #前复权
#hfq = ts.get_h_data('002337', autype='hfq', start='2016-08-01', end='2016-08-05') #后复权
#df = ts.get_h_data('002337', autype=None, start='2016-08-01', end='2016-08-05') #不复权
#df2 = ts.get_h_data('hs300', start='2016-08-01', end='2016-08-05')

#df3 = df = ts.get_hist_data('002337', start='2016-08-01', end='2016-08-05')

#print hfq
#print "---\r\n"
#print df
#print "---\r\n"
#print df2
#print "---\r\n"
#print df3


import pymongo
conn = pymongo.MongoClient('192.168.1.83', port=27017)
stockdb = conn.etomc2.stockDB
for post in stockdb.find({'600808_hfq': {'$exists':1}},{'600808_hfq':1,"_id":0}):
    for val in post.items():
        for v in val[1]:
            print v

