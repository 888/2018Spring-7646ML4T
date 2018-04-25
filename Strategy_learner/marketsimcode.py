#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:20:55 2018

@author: cxue1
"""

import pandas as pd
import numpy as np
import datetime as dt
from util import get_data, plot_data
import matplotlib.pyplot as plt

def author(self):
    return 'cxue34'
#marketsim function to get new portfolio based on orders
def compute_portvals(df, sd, ed, start_val = 100000, commission=0, impact=0.00):
    # this is the function the autograder will call to test your code
    # NOTE: orders_file may be a string, or it may be a file object. Your
    # code should work correctly with either input
    # TODO: Your code here

    # In the template, instead of computing the value of the portfolio, we just
    # read in the value of IBM over 6 months


    #get start date, end date of order book
    df_orders = pd.DataFrame(df)
    df_orders = df_orders.sort_index()
    df_orders.index=pd.to_datetime(df_orders.index)

    #get start date, end date of order book
    start_date = sd
    end_date = ed
    symbols_list=df_orders['Symbol'].unique()
    dates=pd.date_range(start_date,end_date)
    df_stock_prices=get_data(symbols_list.tolist(), dates)
    df_stock_prices.fillna(method='ffill')
    df_stock_prices.fillna(method='bfill')    
    
    df_stock_prices['cash']=1
    df_trading=df_stock_prices.copy()*0.0
    df_trading.iloc[0]['cash']=start_val
    for order_index, order_row in df_orders.iterrows():
        symble_order=order_row[0]
        price_order=df_stock_prices.loc[order_index][symble_order]
        share_order=order_row[2]
        if order_row[1]=='BUY':
            trade = 1 #trade:buy
        elif order_row[1]=='SELL':
            trade = -1 #trade:sell
        else:
            trade = 0
        df_trading.loc[order_index, symble_order] += share_order*trade
        cost=commission+impact*share_order*price_order
        df_trading.loc[order_index, 'cash'] += share_order*price_order*trade*(-1)-cost
    df_trading.iloc[:,1:]=df_trading.cumsum()
    df_port_vals=df_stock_prices*df_trading
    df_port_vals['port_val']=df_port_vals.sum(axis=1)
    df_port_vals['daily_returns']=(df_port_vals['port_val'][1:]/df_port_vals['port_val'][:-1].values)-1 #or use shift
    df_port_vals['daily_returns'][0]=0
    def assess_port(df, rfr, sf):
        # Get portfolio statistics (note: std_daily_ret = volatility)
        # code for stats
        cr = (df.iloc[-1, -2] / df.iloc[0, -2])-1

        # adr
        adr = df["daily_returns"][1:].mean()

        # sddr, std deviation of daily returns
        sddr = df["daily_returns"][1:].std()

        # Sharpe Ratio
        sr = (sf ** 0.5) * (adr - rfr) / sddr

        # Compare daily portfolio value with SPY using a normalized plot

        return cr, adr, sddr, sr

    cr, adr, sddr, sr= assess_port(df_port_vals,rfr=0,sf=252)
    port_val=df_port_vals.iloc[:,-2]
    #return port_val, cr, adr, sddr
    return df_port_vals['daily_returns'], cr, port_val
