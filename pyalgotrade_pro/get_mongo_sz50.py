import pymongo


ret = []

conn = pymongo.MongoClient('127.0.0.1', port=27017)
print(conn.sz50.collection_names())
szCode = conn.sz50["sz50_601601"]
for post in szCode.find():
    for key, val in post.items():
        if key == '_id':
            continue
        print(val['high'])
