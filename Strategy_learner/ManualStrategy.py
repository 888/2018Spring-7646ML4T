#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:22:32 2018

@author: cxue1
"""

import pandas as pd
import numpy as np
import datetime as dt
from util import get_data
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import marketsimcode as msc

class ManualStrategy(object):    
    def __init__(self):
        pass
    def get_prices(self, symbol = 'JPM', sd = dt.datetime(2008,1,1), ed = dt.datetime(2009,12,31), sv=1000000):
        # Read in adjusted closing prices for given symbols, date range
        syms = [symbol]
        # Read in adjusted closing prices for given symbols, date range
        dates = pd.date_range(sd, ed)
        prices_all = get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        return prices
    #functions used for all methods to generate orders
    def deliver_shares(self, df):
        if df == 'BUY':
            val = 1
        elif df == 'SELL':
            val = -1
        else:
            val =0
        return val
    
    def shares(self, df):
        if df == 2 or df == -2:
            val = 2000
        else:
            val = 0
        return val
    
    #1 benchmark order
    def get_benchmark(self, prices, sd, ed):
        prices_benchmark = prices.copy()
        prices_benchmark = prices_benchmark/prices_benchmark.iloc[0]
        symbol=prices.columns[0]
        benchmark={'Date': prices.index[0],'Symbol':[symbol]}
        benchmark_order=pd.DataFrame(benchmark)
        benchmark_order['Order']='BUY'
        benchmark_order['Shares']=1000
        benchmark_order.set_index('Date', inplace=True)
        benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr=msc.compute_portvals(benchmark_order, sd, ed, start_val = 100000, commission=9.95, impact=0.005)
        return benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr
    
    #2 Manual Strategy
    #2 BB
    def get_BB(self, prices,sd, ed):
        prices_BB = prices.copy()
        t_SMA=20
        prices_BB['SMA']=pd.rolling_mean(prices_BB['JPM'], window=t_SMA)
        t_std=10
        prices_BB['std']=pd.rolling_std(prices_BB['JPM'], window=t_std)
        
        prices_BB['up_line']=prices_BB['SMA']+2*prices_BB['std']
        prices_BB['down_line']=prices_BB['SMA']-2*prices_BB['std']
       
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
        prices_BB['deliver_Shares'] = prices_BB['Order'].apply(self.deliver_shares)  
        prices_BB['deliver_Shares2']=prices_BB['deliver_Shares'].diff()
        prices_BB['Shares']=prices_BB['deliver_Shares2'].apply(self.shares)
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
    
        BB_val, BB_cr, BB_adr, BB_sddr=msc.compute_portvals(BB_order, sd, ed, start_val = 100000, commission=9.95, impact=0.005)
        return BB_order, BB_val, BB_cr, BB_adr, BB_sddr



    def testPolicy(self,symbol = "JPM", sd=dt.datetime(2009,1,1), ed=dt.datetime(2011,12,31), sv = 100000):
        self.symbol=symbol
        self.sd=sd
        self.ed=ed
        self.sv=sv
        prices=self.get_prices(symbol, sd, ed, sv)
        BB_order, BB_val, BB_cr, BB_adr, BB_sddr=self.get_BB(prices,sd, ed)
        return BB_order

def test_code():
    ms=ManualStrategy()
    df_trades = ms.testPolicy(symbol="JPM", sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,12,31), sv=100000)
    symbol="JPM"
    sd=dt.datetime(2008,1,1) #change to 2010,1,1for test
    ed=dt.datetime(2009,12,31) #change to 2011,12,31 for test
    sv=100000
    prices=ms.get_prices(symbol, sd, ed, sv)
    benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr=ms.get_benchmark(prices, sd, ed)
    BB_order, BB_val, BB_cr, BB_adr, BB_sddr=ms.get_BB(prices, sd, ed)
    BUY_lines=BB_order[BB_order['Order']=='BUY']
    SELL_lines=BB_order[BB_order['Order']=='SELL']
    all_data=pd.DataFrame(benchmark_val)
    all_data['BB_val']=BB_val
    all_data.rename(columns={"port_val": "benchmark_val"}, inplace=True)
    all_data = all_data/all_data.iloc[0]
    benchmark_line=plt.plot(all_data['benchmark_val'], c='b', label='Benchmark')
    BB_line=plt.plot(all_data['BB_val'], c='black', label='BB')
    plt.title('Benchmark vs ManualStrategy')
    plt.xlabel('time')
    plt.xticks(rotation=45)
    plt.ylabel('Portfolio')
    for x in BUY_lines.index:
        plt.axvline(x, color='green')
    for x in SELL_lines.index:
        plt.axvline(x, color='red')
    plt.legend()
    plt.show()
    plt.savefig('indicator_manual')
    print "Cumulative return of benchmark: ", benchmark_cr, ", Cumulative return of manual strategy: ", BB_cr
    

if __name__=="__main__":
    test_code()







