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
import pandas as pd

df500 = ts.get_zz500s()
df300 = ts.get_hs300s()

df800 = pd.DataFrame(df500)
df800 = df800.append(df300,ignore_index=True)
df800.sort_values(by="code")

un800 = json.loads(df800.to_json(orient="records"))
conn = pymongo.MongoClient('192.168.1.83', port=27017)
conn.etomc2["un800"].insert(un800)
