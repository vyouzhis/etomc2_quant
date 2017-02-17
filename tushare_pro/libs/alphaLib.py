#!/usr/bin/python2
# -*- coding: utf-8 -*-
# alphaLib
#
# use alphaLib
#
# vim:fileencoding=utf-8:sw=4:et -*- coding: utf-8 -*-
#
from mongo_data import MonSQLDatabase
import pandas as pd
import numpy as np

class alphaLib():
    def __init__(self, code=None):
        """
        __init__
        Parameters
        ---------
        code:string  股票代码
        """

        if code is None:
            code = "hs300"
        self.__code = code

    def Alpha(self, rts):
        """
        Alpha 数据结构
        Parameters
        ---------
        rts:DataFrame 需要计算股票的 df 数据

        Return
        -------
        DataFrame
            beta, beta 值
            alpha, alpha 值
            r_squared, R 次方
            volatility, 波动率
            momentum, 动量
        """
        mongo = MonSQLDatabase()

        mongo.getBars(self.__code)
        rbts = mongo.getDF()

        dfsm = pd.DataFrame({'s_adjclose' : rts['Adj Close'],
                                                    'b_adjclose' : rbts['Adj Close']},
                                                    index=rts.index)

# compute returns
        dfsm[['s_returns','b_returns']] = dfsm[['s_adjclose','b_adjclose']]/\
                dfsm[['s_adjclose','b_adjclose']].shift(1) -1
        dfsm = dfsm.dropna()
        covmat = np.cov(dfsm["s_returns"],dfsm["b_returns"])

# calculate measures now
        beta = covmat[0,1]/covmat[1,1]
        alpha= np.mean(dfsm["s_returns"])-beta*np.mean(dfsm["b_returns"])

# r_squared     = 1. - SS_res/SS_tot
        ypred = alpha + beta * dfsm["b_returns"]
        SS_res = np.sum(np.power(ypred-dfsm["s_returns"],2))
        SS_tot = covmat[0,0]*(len(dfsm)-1) # SS_tot is sample_variance*(n-1)
        r_squared = 1. - SS_res/SS_tot
# 5- year volatiity and 1-year momentum
        volatility = np.sqrt(covmat[0,0])
        momentum = np.prod(1+dfsm["s_returns"].tail(12).values) -1

# annualize the numbers
        prd = 12. # used monthly returns; 12 periods to annualize
        alpha = alpha*prd
        volatility = volatility*np.sqrt(prd)
        alphas={}
        alphas["beta"] = "%.3f"%(beta)
        alphas["alpha"] = "%.3f"%(alpha*100)
        alphas["r_squared"] = r_squared
        alphas["volatility"] = volatility
        alphas["momentum"] = momentum
        adf = pd.Series(alphas).to_frame().T

        return adf
