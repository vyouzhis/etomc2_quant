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
#回测时间
        self._Day = 330
        self._NextDay = 20
        # 代码
        self._Code = None
#
        self._pastCodeKline = {}

#默认组合数量
        self._maxYT = 5

        #保存当前交易的代码, 每 _Day 记录一次
# code 股票代码，sdate,开始时间，edate 结束时间，close 收盘价格，hfqclose hfq
# 收盘价格, returns 收益，types 是不是已经结束了, team _Day 的组合
        self._col = ['code','sdate','edate','close','hfqclose','returns','types','team']

        self._TraderCodeList = pd.DataFrame(columns=self._col)
# 更换的时候，把所有负收益都去掉

        self._AllLoss = True


    def setAllLoo(self, flag):
        """
            设置对换数量
        Parameters
        ----------
        flag:boolen  default True

        """
        self._AllLoss = flag

    def setDay(self, day):
        self._Day = day

    def setCode(self, code):
        self._Code = code

    def getTraderCodeList(self):
        return self._TraderCodeList

    def getRange(self,tol, cl):
        """
            获取随机数
        Parameters
        ----------
            tol:int  len(cl)
            cl:list  codelist
        Return
        -------
            p:int  cl index
        """
        p = 0
        tcl = self._TraderCodeList[self._TraderCodeList.types == 1]
        while True:
            p = random.randint(0, tol-1)
            code = cl[p]["code"]
            if tcl[tcl.code == code].code.count() == 0:
                break
        return p

    def FindKline(self, iday, code):
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
        kline = kp.getOrderDateKLine(code, iday, 1)

        return kline

    def FindQuant(self, kline, date, code):
        """
        Parameters
        ---------
            kline:DataFrame
            date: date
            code:String
        Return
        ------
            None
            False
            True
        """
        runCode = self._TraderCodeList[self._TraderCodeList.types == 1]
        runCode = runCode[runCode.code == code]
#        kline = self.FindKline(iday,runCode.code.values[0])
        qm = quantMaKline()
        qm.setmal(self._NextDay)
        flag = None
        if kline is not None:
            nextDateIndex = kline[kline.date == date]
            if nextDateIndex.date.count() == 0:
                return flag
            onlyDay = kline[kline.index == nextDateIndex.index[0]]

            if code in self._pastCodeKline:
                pck = self._pastCodeKline[code]
                flag = qm.quantma(onlyDay, pck)
            else:
                flag = qm.quantma(onlyDay)

            self._pastCodeKline[code] = onlyDay
        return flag

    def TheLastLoss(self, returns=0):
        """
            找出收益最差的几个
        Parameters
            returns:float 收益极值
        ---------
        Return
        --------
            list
        """
        if self._AllLoss == False:
            loss = self._TraderCodeList[self._TraderCodeList.types == 1].sort_values(by="returns")

            code = loss.head(1).code.values[0]
            self._TraderCodeList.loc[(self._TraderCodeList['code'] == code) &
                                     (self._TraderCodeList["types"] == 1), 'types'] = 0
        else:
            loss = self._TraderCodeList[self._TraderCodeList.types == 1]
            loss = loss[loss.returns < returns]
            for code in loss.code.values:
                self._TraderCodeList.loc[(self._TraderCodeList['code'] == code) &
                                     (self._TraderCodeList["types"] == 1), 'types'] = 0

    def UpdateReturns(self, iday):
        runCode = self._TraderCodeList[self._TraderCodeList.types == 1]
        #print runCode
        if runCode.code.count() == 0:
            return

        for rc in runCode.itertuples():

            code = rc.code
            khfqline = self.FindKline(iday, code+"_hfq")
            if khfqline is None:
                continue
            khfqline = khfqline[khfqline.date == iday]
            if khfqline.close.count()==0:
                continue

            close = khfqline.close.values[0]
            preclose = rc.hfqclose
            returns =(close - preclose)/close*100

            self._TraderCodeList.loc[(self._TraderCodeList['code'] == code) &
                                     (self._TraderCodeList["types"] == 1), 'returns'] = returns
            self._TraderCodeList.loc[(self._TraderCodeList['code'] == code) &
                                     (self._TraderCodeList["types"] == 1), 'edate'] = iday

    def StockTrade(self):
        startDay = time()-86400*self._Day
        NowTime = strftime("%Y-%m-%d", localtime(startDay))
        kp = kPrice()
        hs3t = kp.HS300Time(NowTime)
        qm = quantMaKline()
        qm.setmal(20)
        ga = getAllStock()
        codelist = None

        if self._Code is not None:
            codelist = ga.getIndustryCode(self._Code)
        else:
            codelist = ga.getUn800()
        #tol = len(codelist)

        step = 0
        team = 1
        for iday in hs3t:

            self.UpdateReturns(iday)

            #sell every 13 day
            if step == self._NextDay:
                team += 1
                self.TheLastLoss()
                step = 0
            else:
                self.TheLastLoss(-2)
            """
            #sell
            for sc in TraderCodeList:
                sflag = self.FindQuant(i, sc)
                if sflag == False:
                    # quant
                    TraderCodeList.pop(sc)
                    sdf = pd.Series([bcode,day.ds, day.de, sclose,eclose, term, 1, i, diff], index=col)
                    stockDF = stockDF.append(sdf, ignore_index=True)

                # return < -5
                ctmp = buyList[-1]
                returns =(hfqDayK.close.values[0] - ctmp.close.values[0])/hfqDayK.close.values[0]*100
                if returns < -5:
                    TraderCodeList.pop(sc)
                    sdf = pd.Series([bcode,day.ds, day.de, sclose,eclose, term, 1, i, diff], index=col)
                    stockDF = stockDF.append(sdf, ignore_index=True)

            """
            #buy
            for cd in codelist:
                # 组合股票数
                if self._TraderCodeList[self._TraderCodeList.types == 1].types.count() == self._maxYT:
                    break

                #p = self.getRange(tol, codelist)
                code = cd["code"]
                kline = kp.getOrderDateKLine(code, iday, 1)
                if kline is None:
                    continue
                khfqline = kp.getOrderDateKLine(code+"_hfq", iday, 1)
                if khfqline is None:
                    continue
                bflag = self.FindQuant(kline, iday, code)
                if bflag == False:
#col = ['code','sdate','edate','close','hfqclose','returns','types','team']
                    nextDateIndex = khfqline[khfqline.date == iday]
                    if nextDateIndex.close.count()==0:
                        continue
                    hfqDay = khfqline[khfqline.index == nextDateIndex.index[0]]
                    pdser = pd.Series([code, hfqDay.date.values[0], 0, kline.close.values[0] ,
                                       hfqDay.close.values[0], 0, 1, team],index=self._col)

                    self._TraderCodeList = self._TraderCodeList.append(pdser,ignore_index=True)

                    continue

            step+=1


def main():

    if(len(sys.argv) == 2):
        code = sys.argv[1]
        yt = YangTuo()
        yt.setCode(code)
        yt.StockTrade()
        rest = yt.getTraderCodeList()
        print rest.sort_values(by="returns")
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
        print "3"
        #yt = YangTuo()
        #yt.StockTrade()

if __name__ == "__main__":
    main()
