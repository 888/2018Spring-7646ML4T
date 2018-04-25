#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:19:36 2018

@author: cxue1
"""

import pandas as pd
import numpy as np
import datetime as dt
from util import get_data, plot_data
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import marketsimcode as msc


def get_prices(sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,12,31), syms = ['JPM'], sv=1000000):
    
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    return prices

def deliver_shares(df):
    if df == 'BUY':
        val = 1
    elif df == 'SELL':
        val = -1
    else:
        val =0
    return val

def shares(df):
    if df == 2 or df == -2:
        val = 2000
    else:
        val = 0
    return val

#1 momentum
def get_momentum(prices,gen_plot=False):
    prices_momentum = prices.copy()
    prices_momentum = prices_momentum/prices_momentum.iloc[0]
    t=10
    prices_momentum['momentum']=prices_momentum['JPM']/prices_momentum['JPM'].shift(t)
    #plot graph
    if gen_plot:
        print("Technical Analysis by Momentum: ")
        plot_data(prices_momentum[['JPM','momentum']], title="Method-1 momentum", xlabel="Date", ylabel="Price")
        plt.savefig('indicator_momentum')
    """
    #get momentum order
    def momentum_order(df):
        if df > 1.3 :
            val = 'SELL'
        elif df <= 0.7:
            val = 'BUY'
        else:
            val = 0
        return val
    prices_momentum['Order'] = prices_momentum['momentum'].apply(momentum_order)
    prices_momentum=prices_momentum[prices_momentum['Order'] !=0 ]
    prices_momentum['deliver_Shares'] = prices_momentum['Order'].apply(deliver_shares)  
    prices_momentum['deliver_Shares2']=prices_momentum['deliver_Shares'].diff()
    prices_momentum['Shares']=prices_momentum['deliver_Shares2'].apply(shares)
    mo_Shares=prices_momentum['Shares'].tolist()
    mo_Shares[0]=1000
    prices_momentum['Symbol']='JPM'
    momentum_order=pd.DataFrame(prices_momentum, columns=['Symbol','Order'])
    momentum_order['Shares']=np.asarray(mo_Shares)
    momentum_order.index.name='Date'
    momentum_order=momentum_order[momentum_order.Shares != 0]
    momentum_val, cr, adr, sddr=msc.compute_portvals(momentum_order, start_val = 100000, commission=0, impact=0.00)
    """

#2 SMA
def get_SMA(prices,gen_plot=False):
    prices_SMA = prices.copy()
    prices_SMA = prices_SMA/prices_SMA.iloc[0]
    t=14
    prices_SMA['SMA']=pd.rolling_mean(prices_SMA['JPM'], window=t)
    prices_SMA['d_SMA']=prices_SMA['JPM']/prices_SMA['SMA']-1

    #plot graph
    if gen_plot:
        print("Technical Analysis by SMA: ")
        plot_data(prices_SMA[['JPM','SMA','d_SMA']], title="Method-2 SMA", xlabel="Date", ylabel="Price")
        plt.savefig('indicator_SMA')

    """
    #get SMA order
    def SMA_order(df):
        if df > 0.20 :
            val = 'SELL'
        elif df <= -0.20:
            val = 'BUY'
        else:
            val = 0
        return val
    prices_SMA['Order'] = prices_SMA['d_SMA'].apply(SMA_order)
    prices_SMA=prices_SMA[prices_SMA['Order'] !=0 ]
    prices_SMA['deliver_Shares'] = prices_SMA['Order'].apply(deliver_shares)  
    prices_SMA['deliver_Shares2']=prices_SMA['deliver_Shares'].diff()
    prices_SMA['Shares']=prices_SMA['deliver_Shares2'].apply(shares)
    SMA_Shares=prices_SMA['Shares'].tolist()
    SMA_Shares[0]=1000
    prices_SMA['Symbol']='JPM'
    SMA_order=pd.DataFrame(prices_SMA, columns=['Symbol','Order'])
    SMA_order['Shares']=np.asarray(SMA_Shares)
    SMA_order.index.name='Date'
    SMA_order=SMA_order[SMA_order.Shares != 0]
    SMA_val, cr=compute_portvals(SMA_order, start_val = 100000, commission=0, impact=0.00)
    print ("cumulative return by SMA: ", cr)
    print ()
    return SMA_val, cr
    """
#3 BB
def get_BB(prices,gen_plot=False):
    prices_BB = prices.copy()
    t_SMA=20
    prices_BB['SMA']=pd.rolling_mean(prices_BB['JPM'], window=20)
    t_std=10
    prices_BB['std']=pd.rolling_std(prices_BB['JPM'], window=10)
    prices_BB['up_line']=prices_BB['SMA']+2*prices_BB['std']
    prices_BB['down_line']=prices_BB['SMA']-2*prices_BB['std']
    #plot graph
    if gen_plot:
        print("Technical Analysis by Bollinger bands: ")
        plot_data(prices_BB[['JPM','SMA','up_line','down_line']], title="Method-3 Bollinger bands", xlabel="Date", ylabel="Price")
        plt.savefig('indicator_BB')

    """
    #get BB order
    for order_index, order_row in prices_BB.iterrows():
        upline_price=order_row[-2]
        downline_price=order_row[-1]
        price=order_row[0]
        if price > upline_price:
            trade = 'SELL' 
        elif price < downline_price:
            trade = 'BUY'
        else:
            trade = 0
        prices_BB.loc[order_index, 'Order'] = trade
    prices_BB=prices_BB[prices_BB['Order'] !=0 ] 
    prices_BB['deliver_Shares'] = prices_BB['Order'].apply(deliver_shares)  
    prices_BB['deliver_Shares2']=prices_BB['deliver_Shares'].diff()
    prices_BB['Shares']=prices_BB['deliver_Shares2'].apply(shares)
    BB_Shares=prices_BB['Shares'].tolist()
    BB_Shares.pop(0)
    BB_Shares.append(0)
    prices_BB['Symbol']='JPM'
    BB_order=pd.DataFrame(prices_BB, columns=['Symbol','Order'])
    BB_order['Shares']=np.asarray(BB_Shares)
    BB_order.index.name='Date'
    BB_order=BB_order[BB_order.Shares != 0]
    BB_shares_list=BB_order['Shares'].tolist()
    BB_shares_list[0]=1000
    BB_order['Shares']=BB_shares_list
    BB_val, cr=compute_portvals(BB_order, start_val = 100000, commission=0, impact=0.00)
    print ("cumulative return by BB: ", cr)
    print ()
    return BB_val, cr
    """

#4 RSI
def get_RSI(prices,gen_plot=False):
    prices_RSI = prices.copy()
    prices_RSI = prices_RSI/prices_RSI.iloc[0]
    prices_RSI['gain/loss']=prices_RSI['JPM']-prices_RSI['JPM'].shift(1)
    prices_RSI['gain']=prices_RSI['gain/loss'].apply(lambda x: x>0 and x or 0)
    prices_RSI['loss']=prices_RSI['gain/loss'].apply(lambda x: x<0 and x or 0)    
    list_gain=prices_RSI['gain'].tolist()
    list_loss=prices_RSI['loss'].tolist()
    t=7
    list_RS=[]
    for i in range(0,t):
        list_RS.append(np.NAN)
    for i in range(t,prices.shape[0]):
        RS=(np.mean(list_gain[0:i])*(t-1)+list_gain[i])/(np.mean(list_loss[0:i])*(t-1)+list_loss[i])*(-1)
        list_RS.append(RS)
    prices_RSI['RS']=list_RS
    prices_RSI['RSI']=prices_RSI['RS'].apply(lambda x:100-100/(1+x))
    #plot graph
    if gen_plot:
        print("Technical Analysis by RSI: ")
        plot_data(prices_RSI[['RSI']], title="Method-4 RSI", xlabel="Date", ylabel="Price")
        plt.savefig('indicator_RSI')

    """
    #get RSI order
    for order_index, order_row in prices_RSI.iterrows():
        RSI=order_row[-1]
        if RSI > 70:
            trade = 'SELL' 
        elif RSI < 30:
            trade = 'BUY'
        else:
            trade = 0
        prices_RSI.loc[order_index, 'Order'] = trade
    prices_RSI=prices_RSI[prices_RSI['Order'] !=0 ]
    prices_RSI['deliver_Shares'] = prices_RSI['Order'].apply(deliver_shares)  
    prices_RSI['deliver_Shares2']=prices_RSI['deliver_Shares'].diff()
    prices_RSI['Shares']=prices_RSI['deliver_Shares2'].apply(shares)
    RSI_Shares=prices_RSI['Shares'].tolist()
    RSI_Shares[0]=1000
    RSI_order=pd.DataFrame(prices_RSI, columns=['Symbol','Order'])
    RSI_order['Symbol']='JPM'
    RSI_order['Shares']=np.asarray(RSI_Shares)
    RSI_order.index.name='Date'
    RSI_order=RSI_order[RSI_order.Shares != 0]
    RSI_val, cr=compute_portvals(RSI_order, start_val = 100000, commission=0, impact=0.00)
    print ("cumulative return by RSI: ", cr)
    print ()
    return RSI_val, cr
    """

#5 MACD
def get_MACD(prices,gen_plot=False):
    prices_MACD = prices.copy()
    prices_MACD = prices_MACD/prices_MACD.iloc[0]
    t1=10
    t2=20
    prices_MACD['SMA']=pd.rolling_mean(prices_MACD['JPM'], window=t1)
    list_SMA=prices_MACD['SMA'].tolist()
    list_JPM=prices_MACD['JPM'].tolist()
    list_EMA1=[]
    list_EMA2=[]
    multiplier1=2.0/(t1+1)
    multiplier2=2.0/(t2+1)
    EMA_start1=list_SMA[t1-1]
    EMA_start2=list_SMA[t2-1]
    for i in range(0,t1-1):
        list_EMA1.append(np.NAN)
    list_EMA1.append(EMA_start1)
    for i in range(t1,prices.shape[0]):
        EMA=(list_JPM[i]-list_EMA1[-1])*multiplier1+list_EMA1[-1]
        list_EMA1.append(EMA)
    for i in range(0,t2-1):
        list_EMA2.append(np.NAN)
    list_EMA2.append(EMA_start2)
    for i in range(t2,prices.shape[0]):
        EMA=(list_JPM[i]-list_EMA2[-1])*multiplier2+list_EMA2[-1]
        list_EMA2.append(EMA)
    prices_MACD['EMA'+str(t1)]=list_EMA1
    prices_MACD['EMA'+str(t2)]=list_EMA2
    
    #plot graph
    if gen_plot:
        print("Technical Analysis by MACD: ")
        plot_data(prices_MACD[['EMA'+str(t1), 'EMA'+str(t2)]], title="MACD", xlabel="Date", ylabel="Price")
        plt.savefig('indicator_MACD')

    """
    #get RSI order
    for order_index, order_row in prices_MACD.iterrows():
        EMA_L=order_row[-1]
        EMA_S=order_row[-2]
        if EMA_S > EMA_L:
            trade = 'BUY' 
        elif EMA_S < EMA_L:
            trade = 'SELL'
        else:
            trade = 0
        prices_MACD.loc[order_index, 'Order'] = trade
    prices_MACD=prices_MACD[prices_MACD['Order'] !=0 ]
    prices_MACD['deliver_Shares'] = prices_MACD['Order'].apply(deliver_shares)  
    prices_MACD['deliver_Shares2']=prices_MACD['deliver_Shares'].diff()
    prices_MACD['Shares']=prices_MACD['deliver_Shares2'].apply(shares)
    shares_MACD=prices_MACD['Shares'].tolist()
    shares_MACD[0]=1000
    MACD_order=pd.DataFrame(prices_MACD, columns=['Symbol','Order'])
    MACD_order['Symbol']='JPM'
    MACD_order['Shares']=np.asarray(shares_MACD)
    MACD_order.index.name='Date'
    MACD_order=MACD_order[MACD_order.Shares != 0]
    MACD_val, cr=compute_portvals(MACD_order, start_val = 100000, commission=0, impact=0.00)
    print ("cumulative return by MACD: ", cr)
    print ()
    return MACD_val, cr
    """

def test_code():
    # This code WILL NOT be tested by the auto grader
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!
    sd = dt.datetime(2008,1,1)
    ed = dt.datetime(2009,12,31)
    symbols = ['JPM']
    start_val = 1000000  

    # Assess the dataset
    prices = get_prices(sd, ed, symbols, start_val)
    
    #1 momentum
    get_momentum(prices, gen_plot=True)
    
    #2 SMA
    get_SMA(prices, gen_plot=True)

    
    #3 BB
    get_BB(prices, gen_plot=True)

    #4 RSI
    get_RSI(prices, gen_plot=True)

    #5 MACD
    get_MACD(prices, gen_plot=True)

if __name__=="__main__":
    test_code()
