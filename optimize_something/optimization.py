"""MC1-P2: Optimize a portfolio.

Copyright 2017, Georgia Tech Research Corporation
Atlanta, Georgia 30332-0415
All Rights Reserved
"""
import pandas as pd
import numpy as np
import datetime as dt
import scipy.optimize as spo
#import matplotlib.pyplot as plt
#plt.style.use('ggplot')
from util import get_data, plot_data

# This is the function that will be tested by the autograder
# The student must update this code to properly implement the functionality
def optimize_portfolio(sd=dt.datetime(2008,1,1), ed=dt.datetime(2009,1,1), \
    syms=['GOOG','AAPL','GLD','XOM'], gen_plot=False):
    sv=1000000
    rfr=0.0
    sf=252.0
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    # Get daily portfolio value
    prices_norm=prices/prices.iloc[0,:]
    prices_SPY = prices_all['SPY']

    guess_list=len(syms)*[1./len(syms),]
    #nested function for minimizing
    def compute_portfolio_stat(allocs_f):
        prices_alloc_f=prices_norm*allocs_f
        pos_vals_f=prices_alloc_f*sv
        port_val_f=pos_vals_f.sum(axis=1)
        cr_f=port_val_f[-1]/port_val_f[0]-1
        daily_ret_f=port_val_f.copy()
        daily_ret_f[1:]=port_val_f[1:]/port_val_f[:-1].values-1
        daily_ret_f[0]=0
        sddr_f=daily_ret_f[1:].std()
        return sddr_f

    cons=({'type':'eq', 'fun':lambda x: np.sum(x)-1})
    bnds = tuple((0,1.0) for i in range(len(syms)))
    minimize_result = spo.minimize(compute_portfolio_stat, 
                                   guess_list, 
                                   method='SLSQP', 
                                   bounds=bnds,
                                   options={'disp':True},
                                   constraints=cons)
    
    
    allocs=minimize_result.x.tolist()
    prices_alloc=prices_norm*allocs
    pos_vals=prices_alloc*sv
    port_val=pos_vals.sum(axis=1)
    cr=port_val[-1]/port_val[0]-1
    daily_ret=port_val.copy()
    daily_ret[1:]=port_val[1:]/port_val[:-1].values-1
    daily_ret[0]=0
    adr=daily_ret[1:].mean()
    sddr=daily_ret[1:].std()
    sr=(sf**0.5)*(adr-((1.0+rfr)**(1/sf)-1))/sddr
    ev=port_val[-1]
    # Compare daily portfolio value with SPY using a normalized plot
    #if gen_plot:
        # add code to plot here
    #    df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
    #    df_temp_norm = df_temp/df_temp.iloc[0]
    #   plot_data(df_temp_norm, title="Daily Portfolio and SPY", xlabel="Date", ylabel="Normalized Price")
    return allocs, cr, adr, sddr, sr
def test_code():
    # This function WILL NOT be called by the auto grader
    # Do not assume that any variables defined here are available to your function/code
    # It is only here to help you set up and test your code

    # Define input parameters
    # Note that ALL of these values will be set to different values by
    # the autograder!

    start_date = dt.datetime(2009,1,1)
    end_date = dt.datetime(2010,1,1)
    symbols = ['GOOG', 'AAPL', 'GLD', 'XOM', 'IBM']

    # Assess the portfolio
    allocations, cr, adr, sddr, sr = optimize_portfolio(sd = start_date, ed = end_date,\
        syms = symbols, \
        gen_plot = False)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocations
    print "Sharpe Ratio:", sr
    print "Volatility (stdev of daily returns):", sddr
    print "Average Daily Return:", adr
    print "Cumulative Return:", cr

if __name__ == "__main__":
    # This code WILL NOT be called by the auto grader
    # Do not assume that it will be called
    test_code()
