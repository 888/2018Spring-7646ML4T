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

class BestPossibleStrategy(object):    
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
        benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr=msc.compute_portvals(benchmark_order, sd, ed, start_val = 100000, commission=0, impact=0.00)
        return benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr
    
    #2 BPS
    def get_bps(self, prices, sd, ed):
        prices_bps = prices.copy()
        prices_bps = prices_bps/prices_bps.iloc[0]
       
        #get bps order
        symbol=prices_bps.columns[0]
        prices_bps['Symbol']=symbol
        prices_bps['compare']=prices_bps[symbol]-prices_bps[symbol].shift(1) 
        prices_bps['d_price']=prices_bps['compare'].shift(-1)
        def buy_sell(df):
            if df > 0:
                val = 'BUY'
            elif df < 0:
                val = 'SELL'
            else:
                val = 0
            return val
        prices_bps['Order'] = prices_bps['d_price'].apply(buy_sell)
        prices_bps['deliver_Shares'] = prices_bps['Order'].apply(self.deliver_shares)  
        prices_bps['deliver_Shares2']=prices_bps['deliver_Shares'].diff()
        prices_bps['Shares']=prices_bps['deliver_Shares2'].apply(self.shares)    
        ls_Shares=prices_bps['Shares'].tolist()
        ls_Shares[0]=1000
        
        bps_order=pd.DataFrame(prices_bps, columns=['Symbol','Order'])
        bps_order['Shares']=np.asarray(ls_Shares)
        bps_order.index.name='Date'
        bps_order=bps_order[bps_order.Shares != 0]
        bps_val, bps_cr, bps_adr, bps_sddr=msc.compute_portvals(bps_order, sd, ed, start_val = 100000, commission=0, impact=0.00)
        return bps_order, bps_val, bps_cr, bps_adr, bps_sddr

    def testPolicy(self,symbol = "JPM", sd=dt.datetime(2009,1,1), ed=dt.datetime(2011,12,31), sv = 100000):
        self.symbol=symbol
        self.sd=sd
        self.ed=ed
        self.sv=sv
        syms = [self.symbol]
        prices=self.get_prices(symbol, sd, ed, sv)
        bps_order, bps_val, bps_cr, bps_adr, bps_sddr=self.get_bps(prices, sd, ed)
        return bps_order

def test_code():
    bps=BestPossibleStrategy()
    df_trades = bps.testPolicy(symbol="JPM", sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,12,31), sv=100000)
    symbol="JPM"
    sd=dt.datetime(2008,1,1)
    ed=dt.datetime(2009,12,31)
    sv=100000
    prices=bps.get_prices(symbol, sd, ed, sv)
    benchmark_val, benchmark_cr, benchmark_adr, benchmark_sddr=bps.get_benchmark(prices, sd, ed)
    trade_order, bps_val, bps_cr, bps_adr, bps_sddr=bps.get_bps(prices, sd, ed)
    all_data=pd.DataFrame(benchmark_val)
    all_data['bps_val']=bps_val
    all_data.rename(columns={"port_val": "benchmark_val"}, inplace=True)
    all_data = all_data/all_data.iloc[0]
    #plot
    plt.plot(all_data['benchmark_val'], c='b', label='Benchmark')
    plt.plot(all_data['bps_val'], c='black', label='BPS')
    plt.title('Benchmark vs BestPossibleStrategy')
    plt.xlabel('time')
    plt.xticks(rotation=45)
    plt.ylabel('Portfolio')
    plt.legend()
    plt.show()
    plt.savefig('indicator_bps')
    print "Cumulative return of benchmark: ", benchmark_cr, ", Cumulative return of bps: ", bps_cr
    print "Average daily return of benchmark: ", benchmark_adr, ", Average daily return of bps: ", bps_adr
    print "Standard deviation daily return of benchmark: ", benchmark_sddr, ", Standard deviation daily return of bps: ", bps_sddr


if __name__=="__main__":
    test_code()







