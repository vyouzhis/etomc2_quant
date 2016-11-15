#!/usr/bin/python2
# -*- coding: utf-8 -*-
# mongo_data
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#    alpaca trade stock
#      本策略由一个羊驼类负责每周生成买入卖出信号, 验证羊驼是否名实相符.
#
import pandas as pd
import sys
import random
from time import localtime, strftime, time

from libs.kPrice import kPrice
from libs.kPrice import getAllStock
from libs.quantMaKline import quantMaKline



def getHS300(step):
    """
        以HS300 为标准时间
    """
    kl = kPrice()
    hs300 = kl.getAllKLine("hs300")
    length = hs300.date.count()
    hs300 = hs300.sort_values(by="date")

    dt = {}
    ds = []
    de = []
    for day in range(1, length, step):
        dates = list(hs300[day:day+step].date)

        ds.append(dates[0])
        if len(dates) == step:
            de.append(dates[-1])
        else:
            de.append("")
    dt['ds'] = ds
    dt['de'] = de
    df = pd.DataFrame(data=dt)

    return df



def StockTrade(NumStock, step):
    kl = kPrice()
    tradeDay = getHS300(step)
    bNumlist = []
    allNumlist = []
    un8 = getAllStock()
    clist = un8.getUn800()
    clen = len(clist)

    stockData = {}
    col = ['code','sdate', 'edate','sprice','eprice','term','bs', 'num', 'returns']
    stockDF = pd.DataFrame(columns=col)
    term = 0
    for day in tradeDay.itertuples():

        if term > 0:
            sell = term - 1
            selldf = stockDF[stockDF.term == sell].sort_values(by="returns")
            num = list(selldf[0:1].num)[0]
            bNumlist.remove(num)
            stockDF.loc[(stockDF['num'] == num) & (stockDF["term"] == sell), 'bs'] = 0

        while len(bNumlist) < NumStock:
            r = getRange(clen-1, bNumlist)
            if r in allNumlist:
                continue
            code = clist[r]['code']
            kprice = kl.getAllKLine(code)

            if kprice is None:
                continue

            if term > 0 and quantma(kprice[kprice.date >= day.ds]) == False:
                continue

            sclose = list(kprice[kprice.date == day.ds].close)
            if len(sclose) != 1:
                continue
            stockData[code] = kprice
            bNumlist.append(r)
            allNumlist.append(r)

        for i in bNumlist:
            bcode = clist[i]['code']
            bprice = stockData[bcode]
            sclose = 0
            diff = 0
            dl = list(bprice[bprice.date == day.ds].close)
            if len(dl) == 0:
                #print day.ds
                continue
            else:
                sclose = float(dl[0])

            eclose = 0
            if len(list(bprice[bprice.date == day.de].close)) == 1:
                eclose = float(list(bprice[bprice.date == day.de].close)[0])
                diff = (eclose - sclose)/eclose*100
            sdf = pd.Series([bcode,day.ds, day.de, sclose,eclose, term, 1, i, diff], index=col)
            stockDF = stockDF.append(sdf, ignore_index=True)

        term += 1

    stockDF = stockDF.sort_values(by="term")
    del stockDF["num"]
    print stockDF
    print sum(stockDF.returns)


class YangTuo():
    def __init__(self):
        self._Day = 30
        self._Code = None
        self._pastCodeKline = {}
        self._maxYT = 5

    def setDay(self, day):
        self._Day = day

    def setCode(self, code):
        self._Code = code

    def getRange(self,tol, l):
        """
            获取随机数
        """
        p = random.randint(0, tol)
        while p in l:
            p = random.randint(0, tol)

        return p

    def FindQuant(self, date, code):
        """
            找出该代码的K线
        Parameters
        ---------
            date:date 时间
            code:string  代码
        Return
        -------
            DataFrame
        """
        kp = kPrice()
        qm = quantMaKline()
        qm.setmal(20)
        kline = kp.getOrderDateKLine(code, date, 1)
        if kline is not None:
            nextDateIndex = kline[kline.date == date]
            onlyDay = kline[kline.index == nextDateIndex.index[0]]

            if code in self._pastCodeKline:
                pck = self._pastCodeKline[code]
                print qm.quantma(onlyDay, pck)
            else:
                print qm.quantma(onlyDay)

            self._pastCodeKline[code] = onlyDay

        print "====================="
        return kline

    def StockTrade(self):
        startDay = time()-86400*self._Day
        NowTime = strftime("%Y-%m-%d", localtime(startDay))
        kp = kPrice()
        hs3t = kp.HS300Time(NowTime)
        qm = quantMaKline()
        qm.setmal(20)
        ga = getAllStock()
        cl = None

        TraderCodelist = []


        if self._Code is not None:
            cl = ga.getIndustryCode(self._Code)
        else:
            cl = ga.getUn800()
        tol = len(cl)
        p = self.getRange(tol, TraderCodelist)
        code = cl[p]["code"]

        for i in hs3t:
            #sell
            for sc in TraderCodelist:
                sflag = self.FindQuant(i, sc)
                if sflag == False:
                    # quant
                    TraderCodelist.pop(sc)
                # return < -5
                if returns < -5:
                    TraderCodelist.pop(sc)

            #buy
            for co in cl:
                if co in TraderCodelist:
                    continue
                bflag = self.FindQuant(i, co)
                if bflag == True:
                    TraderCodelist.append(co)

                # 组合股票数
                if len(TraderCodelist) == self._maxYT:
                    break;



def main():

    if(len(sys.argv) == 2):
        code = sys.argv[1]
        yt = YangTuo()
        yt.setCode(code)
        yt.StockTrade()

        """
        pri = test(code)
        print pri


        gc = getAllStock()

        cl = gc.getIndustryCode(code)
        col = ["code","returns", "name"]
        mdf = pd.DataFrame(columns=col)
        for c in cl:

            pri = test(c['code'])
            if pri is None:
                continue
            pdser = pd.Series([c["code"], pri,c['name']],index=col )
            mdf = mdf.append(pdser,ignore_index=True)
        print mdf.sort_values(by="returns")
        print mdf.returns.mean()
        print "right count:%d, sum:%f"%(mdf[mdf.returns > 0].returns.count(), sum(mdf[mdf.returns > 0].returns))
        print "loss count:%d, sum:%f"%(mdf[mdf.returns < 0].returns.count(), sum(mdf[mdf.returns < 0].returns))
        """
        #print "2"
    else:
        yt = YangTuo()
        yt.StockTrade()

if __name__ == "__main__":
    main()
