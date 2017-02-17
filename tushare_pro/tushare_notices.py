#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-

import tushare as ts
import json
import lxml.html
import pandas as pd

from tushare.stock import news_vars as nv
from tushare.stock import cons as ct

from emongo import emongo


class Notice():
    def __init__(self):
        self._code = ""

    def run(self):
        emg = emongo()
        asc = emg.getCollectionNames("AllStockClass")

        clist = asc.find({},{"code":1})
        emg.Close()
        for c in clist:
            cd = c["code"]
        cd = "002723"
        self.getData(cd)

    def get_notices(self,codes=None, page=1):
        '''
        个股信息地雷
        Parameters
        --------
            code:股票代码
            date:信息公布日期

        Return
        --------
            DataFrame，属性列表：
            title:信息标题
            type:信息类型
            date:公告日期
            url:信息内容URL
        '''
        #print codes
        if codes is None:
            return None
        if codes.decode().isdigit():
# 0开头自动补sz，6开头补sh，3开头补sz，否则无效
            if codes.startswith('0'):
                self._code = 'sz' + codes
            elif codes.startswith('6'):
                self._code = 'sh' + codes
            elif codes.startswith('3'):
                self._code = 'sz' + codes
        url = "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=%s&page=%d"%(self._code, page)
        #print url
        html = lxml.html.parse(url)
        res = html.xpath('//table[@class=\"body_table\"]/tbody/tr')
        data = []
        for td in res:
            title = td.xpath('th/a/text()')
            if len(title) > 0:
                title = title[0]
            else:
                continue
            ctype = td.xpath('td[1]/text()')
            if len(ctype) > 0:
                ctype = ctype[0]
            else:
                continue
            date = td.xpath('td[2]/text()')
            if len(date) > 0:
                date = date[0]
            else:
                continue
            url = '%s%s%s'%(ct.P_TYPE['http'], ct.DOMAINS['vsf'], td.xpath('th/a/@href')[0])
            data.append([title, ctype, date, url])
        df = pd.DataFrame(data, columns=nv.NOTICE_INFO_CLS)
        return df

    def getData(self, code):
        df = self.get_notices(code)
        xe = u'回购部分'
        xdf = df[df.title.apply(lambda x: x.find(xe)) != -1]
        if xdf.title.count() > 0:
            print code
            print xdf.title

        d={}
        d[code] = json.loads(df.to_json(orient="records"))
        emg = emongo()
        szNotic = emg.getCollectionNames("StockNotices")

        szNotic.insert(d)
        emg.Close()

def main():
    notice = Notice()
    notice.run()

if __name__ == "__main__":
    main()
