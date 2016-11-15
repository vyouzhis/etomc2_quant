#!/usr/bin/python2
# golden_ratio
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
import pymongo


ret = []
conn = pymongo.MongoClient('127.0.0.1', port=27017)
#print(conn.sz50.collection_names())
szCode = conn.sz50["sz50_601601"].find()
for post in szCode:
    for k in post:
        if k == '_id':
            continue
#        print("%s: %s"%(k, post[k]))
        v = post[k]
        v['time'] = k
        ret.append(v)
        #ret['time'] = k
#for key, val in post.items():

#    print(val['high'])
newlist = sorted(ret, key=lambda k: k['time'])
#print(newlist)
start_len = len(newlist) - 120
price_120 = newlist[start_len:]
low_price = sorted(price_120, key=lambda k:k['high'])[:1]
high_price = sorted(price_120, key=lambda k:k['high'])[119:]

goldenList = [0.191,0.382,0.5,0.618,0.809]

print("%s, %s"%(high_price[0]['high'], high_price[0]['time']))
print("%s, %s"%(low_price[0]['high'], low_price[0]['time']))
print("%s, %s"%(price_120[0]['high'], price_120[0]['time']))
print("%s, %s"%(price_120[119]['high'], price_120[119]['time']))
lowPrice = low_price[0]['high']
highPrice = high_price[0]['high']
updown = True

if(low_price[0]['time'] > high_price[0]['time']):
    updown = False

class Counter(dict):
    def __missing__(self, key):
        return 0

golden = Counter()
for g in price_120:
    if g['high'] <= lowPrice * goldenList[0]:
        golden[goldenList[0]].append(g['high'])
    elif g['high'] > lowPrice * goldenList[0] and g['high'] <= lowPrice * goldenList[1]:
        golden[goldenList[1]].append(g['high'])
    elif g['high'] > lowPrice * goldenList[1] and g['high'] <= lowPrice * goldenList[2]:
        golden[goldenList[2]].append(g)
    elif g['high'] > lowPrice * goldenList[2] and g['high'] <= lowPrice * goldenList[3]:
        golden[goldenList[3]].append(g)
    elif g['high'] > lowPrice * goldenList[3] and g['high'] <= lowPrice * goldenList[4]:
        golden[goldenList[4]].append(g)
    else:
        print(g)
        golden[0].append(g['high'])


print(golden)


