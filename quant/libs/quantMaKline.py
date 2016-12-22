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
import numpy as np

from kPrice import kPrice

class quantMaKline():
    def __init__(self):
        self._col = ["code","date", "close","hfqclose", "mas","mal","returns","type"]
        self._codema = pd.DataFrame(columns=self._col)
#止损 -9%
        self._loss = -9
#止赢 3%
        self._right = 3
#短线 5
        self._mas = 5
#长线 20
        self._mal = 20
# 240 个交易日
        self._Day = 240

        self._DataKLine = None

        self._DataLen = 3

        self._SortTest = {}

        self.InitSortTest()

    def getSortList(self):
        return self._SortTest

    def setDataKLine(self, dk):
        """
            设置K线保存数据
        Parameters
        ---------
            dk:DataFrame
        """
        if self._DataKLine is None:
            self._DataKLine = dk
        else:
            self._DataKLine = self._DataKLine.append(dk,ignore_index=True)
            self._DataKLine = self._DataKLine.sort_values(by="date")
            self._DataKLine = self._DataKLine.tail(self._DataLen)


    def setDataLen(self, len):
        """
            设置K线保存数量
        Parameters
        ----------
            len:int
        """
        self._DataLen = len

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

    def InitSortTest(self):
        for i in range(6):
             self.SortKline(i)

    def SortKline(self, s=0):
        """
          /
         /
        /
        上升,买入
        """
        a = [1,2,3]
        if s == 1:
            """
             /\
            /
             反转下降，缓,观望
            """
            a = [1,3,2]
        elif s == 2:
            """
            \
             \/
            反转上升，缓,观望
            """
            a = [2,3,1]
        elif s == 3:
            """
              /
            \/
            反转上升，急,买入
            """
            a = [2,1,3]
        elif s == 4:
            """
            /\
              \
            反转下降,急,卖出
            """
            a = [3,1,2]
        elif s == 5:
            """
            \
             \
              \
            下降,卖出
            """
            a = [3,2,1]
        df1 = pd.DataFrame({'A':a},index=np.arange(1,4,1))
        df1 = df1.sort_values(by="A")
        self._SortTest[s] = df1.index
        #return df1.index

    def quantma(self):
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
        """

        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)

        if self._DataKLine is None:
            return False

        if self._DataKLine.close.count() != self._DataLen:
            return False
        """
        tmpMsVal = 0
        tmpMlVal = 0

        for kl in self._DataKLine.itertuples():
            if tmpMsVal == 0:
                tmpMsVal = kl[mas].values[0]

            msval = kl[mas].values[0]
            ps = (msval-tmpMsVal)/msval*100
            tmpMsVal = msval

            if tmpMlVal == 0:
                tmpMlVal = kl[mal].values[0]

            mlval = kl[mal].values[0]
            pl = (mlval-tmpMlVal)/mlval*100
            tmpMlVal = mlval

            pdser = pd.Series([ps, pl,],index=col )
            mdf = mdf.append(pdser,ignore_index=True)
            percent.append()
        """

        masIndex = self._DataKLine.sort_values(by=mas).index
        for i in range(6):
            up = self._SortTest[i]
            if masIndex.equals(up) == True and (i == 0 or i == 3):
                return True
            elif masIndex.equals(up) == True and (i == 4 or i == 5):
                return False

        return None

    def quantRun(self):
        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)

        sflag = self.run(mas)
        lflag = self.run(mal)

        if sflag == True and lflag == True:
            return True
        elif sflag == True and lflag == False:
            return True
        elif sflag == False and lflag == True:
            return False
        elif sflag == False and lflag == False:
            return False
        else:
            return None

    def run(self, ma):

        if self._DataKLine is None:
            return False

        if self._DataKLine.close.count() != self._DataLen:
            return False

        maIndex = self._DataKLine.sort_values(by=ma).index
        for i in range(6):
            up = self._SortTest[i]
            if maIndex.equals(up) == True and (i == 0 or i == 3):
                return True
            elif maIndex.equals(up) == True and (i == 4 or i == 5):
                return False

        return None

    def quantSgtL(self):
        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)
        n = 0.1
        ils = [0,2,3]
        rms = self.quantSL(mas, ils)
        ill = [1,2,3,4,5]
        rml = self.quantSL(mal, ill)

        kl = self._DataKLine.sort_values(by="date").tail(2)
        klLast = kl.tail(1)
        kl = kl.head(1)

        sval = kl[mas].values[0]
        lval = kl[mal].values[0]
        m = sval - lval

        if rms in ils and rml in ill and m < n:
            #print "%f , %s"%(m, kl["date"].values[0])
            if klLast[mas].values[0] > klLast[mal].values[0]:
                return True

        rms = self.quantSL(mas, ill)
        rml = self.quantSL(mal, ils)

        if rms in ill and rml in ils and m < n:
            if klLast[mas].values[0] < klLast[mal].values[0]:
                return False

        return None

    def quantSL(self, ma, il):

        if self._DataKLine is None:
            return -1

        if self._DataKLine.close.count() != self._DataLen:
            return -1

        maIndex = self._DataKLine.sort_values(by=ma).index
        for i in range(6):
            up = self._SortTest[i]
            if maIndex.equals(up) == True and (i in il):
                return i

        return -1

    def order(self, code,kl, hfqk, returns, types):
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
        bdate = hfqk.date.values[0]
        bclose = kl.close.values[0]
        bhfqclose = hfqk.close.values[0]
        mas = "ma"+str(self._mas)
        mal = "ma"+str(self._mal)
        bmas = int(hfqk[mas].values[0])
        bmal = int(hfqk[mal].values[0])
        pdser = pd.Series([code, bdate,bclose, bhfqclose, bmas, bmal,"%.02f%%"%returns, types],index=self._col)
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
        self._DataKLine = None

        kl = kPrice()
        kprice = kl.getAllKLine(code)
        if kprice is None:
            print code, " is None"
            return
        hfqprice = kl.getAllKLine(code+"_hfq")
        if hfqprice is None:
            print code, " hfq is None"
            return
        hfqprice["ma5"] = kl.talibMa(hfqprice, 5)
        hfqprice["ma20"] = kl.talibMa(hfqprice, 22)

        if hfqprice is None:
            return None

        startDay = time()-86400*self._Day
        NowTime = strftime("%Y-%m-%d", localtime(startDay))
        kp = kPrice()
        hs3t = kp.HS300Time(NowTime)
        buyList = None
        sb = True
        creturns = 0

        for i in hs3t:
            nextDateIndex = hfqprice[hfqprice.date == i]
            ctmp = None
            kDay = kprice[kprice.date == i]

            if len(nextDateIndex.index) > 0:
                onlyDayK = nextDateIndex.head(1)
                self.setDataKLine(onlyDayK)
                if self._DataKLine.close.count() != self._DataLen:
                    continue

                hfqDayK = hfqprice[hfqprice.date == i].head(1)

                if hfqDayK.date.count() == 0:
                    continue

                flag = self.quantSgtL()
                #flag = self.quantRun()

                if flag == True and sb == True:
                    buyList = hfqDayK
                    self.order(code,kDay, hfqDayK, 0, "buy")

                    sb = False

                if buyList is not None and sb == False:
                    ctmp = buyList
                    returns =(hfqDayK.close.values[0] - ctmp.close.values[0])/hfqDayK.close.values[0]*100
                    if returns > -1 and returns < 2:
                        continue

                    if returns < self._loss:

                        sb = True
                        self.order(code,kDay, hfqDayK,returns, "sell2")
                        creturns += returns
                        buyList = None

                    elif flag == False:
                        sb = True
                        self.order(code,kDay, hfqDayK,returns, "sell")
                        creturns += returns
                        buyList  = None

        if buyList is not None and len(nextDateIndex.index) > 0:
            ctmp = buyList
            #print nextDateIndex
            rs =(nextDateIndex.close.values[0] - ctmp.close.values[0])/nextDateIndex.close.values[0]*100
            self.order(code, kDay, nextDateIndex,rs, "buying")

        return creturns
