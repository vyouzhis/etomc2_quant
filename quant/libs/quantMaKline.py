#!/usr/bin/python2
# -*- coding: utf-8 -*-
# quantMaKline
#
# use mongodb  pyalgotrade  and sz50
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
#     获取股票的基本信息，包括K线，代码等
#
from time import localtime, strftime, time
import pandas as pd

from kPrice import kPrice

class quantMaKline():
    def __init__(self):
        self._col = ["code","date", "close","hfqclose", "mas","mal","returns","type"]
        self._codema = pd.DataFrame(columns=self._col)
#止损 -9%
        self._loss = -9
#短线 5
        self._mas = 5
#长线 20
        self._mal = 20
# 240 个交易日
        self._Day = 240

    def setLoss(self, loss):
        """
            设置止损
        Parameters
        ----------
        loss:int 止损值，尽量是负数
        """
        self._loss = loss

    def setmas(self, ma):
        """
            设置短均线
        Parameters
        ----------
            ma:int 默认 5
        """
        self._mas = ma

    def setmal(self, ma):
        """
            设置长均线
        Parameters
        ----------
            ma:int 默认 10
        """
        self._mal = ma

    def setTradeDay(self, day):
        """
            设置回测交易日
        Parameters
        ----------
            day:int 默认 240
        """
        self._Day = day

    def quantma(self, nowPrice, prePrice=None):
        """
            选择单个股票的基本策略,当5天均线低于10天均线的时候，买入，反之卖出.
        Parameters
        ---------
            nowPrice: DataFrame  当前的K 线数据
            prePrice:DataFrame  前一个交易日的K 线数据
        Return
        -------
            True: 买入
            False: 卖出
        """
        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)

        masval = nowPrice[mas].values[0]
        malval = nowPrice[mal].values[0]
        a = (masval-malval)/masval*100
        p = 0
        n = 0
# 当前一个交易日的K线存在时的参数 百分比
        pm = 3
# 当前一个交易日的K线不存在时的参数 百分比
        am = 2
#卖出时 masval 比 malval高出多少个百分比
        ab = -4
        if prePrice is not None:
            masval = prePrice[mas].values[0]
            malval = prePrice[mal].values[0]
            p = (masval-malval)/masval*100
            n = 1

        if p > pm and a < p:
            # sell
            return False
        elif a > am and n == 0:
            #sell
            return False
        elif a < ab:
            # buy
            return True

    def order(self, code, kl, hfqk, returns, types):
        """
            记录交易细则
        Parameters
        ----------
            code:String 代码
            kl:DataFrame k线数据
            hfqk:DataFrame k线后复权数据
            returns:float 收益
            types:String 买卖
        """
        bdate = kl.date.values[0]
        bclose = kl.close.values[0]
        bhfqclose = hfqk.close.values[0]
        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)
        bmas = kl[mas].values[0]
        bmal = kl[mal].values[0]
        pdser = pd.Series([code, bdate, bclose, bhfqclose, bmas, bmal,returns, types],index=self._col)
        self._codema = self._codema.append(pdser,ignore_index=True)

    def getCodeMa510(self):
        """
            返回交易细则
        Parameters
        -------
        Return
        -------
            DataFrame
        """
        return self._codema

    def makline(self, code):
        """
            均线策略运算
        Parameters
        ---------
            code:string  代码
        Return
        -------

        """
        kl = kPrice()
        kprice = kl.getAllKLine(code)
        hfqprice = kl.getAllKLine(code+"_hfq")
        if kprice is None:
            return None


        startDay = time()-86400*self._Day
        NowTime = strftime("%Y-%m-%d", localtime(startDay))
        kp = kPrice()
        hs3t = kp.HS300Time(NowTime)
        buyList = []
        sellList = []
        sb = True
        creturns = 0
        prePrice = None
        for i in hs3t:
            nextDateIndex = kprice[kprice.date == i]
            ctmp = None

            if len(nextDateIndex.index) > 0:
                onlyDayK = kprice[kprice.index == nextDateIndex.index[0]].head(1)
                hfqDayK = hfqprice[hfqprice.index == nextDateIndex.index[0]].head(1)
                if hfqDayK.date.count() == 0:
                    continue

                flag = self.quantma(onlyDayK, prePrice)

                if flag == True and sb == True:
                    buyList.append(hfqDayK)
                    self.order(code,onlyDayK, hfqDayK, 0, "buy")

                    sb = False


                if len(buyList) > 0:
                    ctmp = buyList[-1]
                    returns =(hfqDayK.close.values[0] - ctmp.close.values[0])/hfqDayK.close.values[0]*100

                    if returns < self._loss and sb == False:
                        #print returns, onlyDayK.date.values[0]
                        sellList.append(onlyDayK)
                        sb = True
                        returns =(hfqDayK.close.values[0] - ctmp.close.values[0])/hfqDayK.close.values[0]*100
                        self.order(code,onlyDayK, hfqDayK,returns, "sell")
                        creturns += returns

                if flag == False and sb == False:
                    ctmp = buyList[-1]
                    returns =(hfqDayK.close.values[0] - ctmp.close.values[0])/hfqDayK.close.values[0]*100

                    sellList.append(onlyDayK)
                    sb = True

                    self.order(code,onlyDayK, hfqDayK,returns, "sell")
                    creturns += returns

                prePrice = onlyDayK

        return creturns
