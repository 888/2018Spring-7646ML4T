"""MC2-P1: Market simulator.

Copyright 2017, Georgia Tech Research Corporation
Atlanta, Georgia 30332-0415
All Rights Reserved
"""

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data, plot_data

def compute_portvals(orders_file = "./orders/orders.csv", start_val = 1000000, commission=9.95, impact=0.005):
    # this is the function the autograder will call to test your code
    # NOTE: orders_file may be a string, or it may be a file object. Your
    # code should work correctly with either input
    # TODO: Your code here

    # In the template, instead of computing the value of the portfolio, we just
    # read in the value of IBM over 6 months


    #get start date, end date of order book
    df_orders = pd.read_csv(orders_file, index_col='Date', parse_dates=True)
    df_orders = df_orders.sort_index()
    df_orders.index=pd.to_datetime(df_orders.index)

    #get start date, end date of order book
    start_date = df_orders.index.values[0]
    end_date = df_orders.index.values[-1]
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
        else:
            trade = -1 #trade:sell
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
    return port_val

def author():
    return 'cxue34' # replace tb34 with your Georgia Tech username.

def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders2.csv"
    sv = 1000000

    # Process orders
    portvals = compute_portvals(orders_file = of, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    
    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = dt.datetime(2008,1,1)
    end_date = dt.datetime(2008,6,1)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

if __name__ == "__main__":
    test_code()
