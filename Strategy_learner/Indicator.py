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

class Indicator(object):
    def __init__(self):
        pass
    def author(self):
        return 'cxue34'
    def get_prices(self, sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,12,31), syms = ['JPM'], sv=1000000):

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
    
    #3 BB
    get_BB(prices, gen_plot=True)

if __name__=="__main__":
    test_code()
