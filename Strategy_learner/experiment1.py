import pandas as pd
import numpy as np
import datetime as dt
import util
import QLearner
import StrategyLearner as sl
import marketsimcode as msc
import random
from util import get_data
import matplotlib.pyplot as plt
plt.switch_backend('agg')

def author(self):
    return 'cxue34'
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

symbol='JPM'
sd = dt.datetime(2008,1,1) 
ed = dt.datetime(2009,12,31) 
sv=1000000
impact=0
import StrategyLearner as sl
learner = sl.StrategyLearner(verbose = False, impact = impact) # constructor
learner.addEvidence(symbol, dt.datetime(2008,1,1), dt.datetime(2009,12,31), sv ) # training phase
df_trades = learner.testPolicy(symbol, sd, ed, sv = 100000) # testing phase

df_order_exp1=df_trades[df_trades['Shares'] !=0]
df_order_exp1['Symbol']=symbol
def deliver_reverse(df):
    if df <0:
        val = 'SELL'
    elif df >0:
        val = 'BUY'
    else:
        val = 'HOLD'
    return val
df_order_exp1['Order']=df_order_exp1['Shares'].apply(deliver_reverse)
df_order_exp1 = df_order_exp1.sort_index()
df_order_exp1.index.name='Date'
df_order_exp1['Shares']=df_order_exp1['Shares'].abs()
df_order_new=pd.DataFrame(df_order_exp1, columns=['Symbol','Order','Shares'])
df_dr, exp1_cr, exp1_val=msc.compute_portvals(df_order_new, sd, ed, start_val = 100000, commission=0.0,impact=impact)

def get_prices(symbol,sd,ed,sv):
    # Read in adjusted closing prices for given symbols, date range
    syms = [symbol]
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(sd, ed)
    prices_all = get_data(syms, dates)  # automatically adds SPY
    prices = prices_all[syms]  # only portfolio symbols
    return prices
#functions used for all methods to generate orders

#1 benchmark order
def get_benchmark(prices, sd, ed):
    prices_benchmark = prices.copy()
    prices_benchmark = prices_benchmark/prices_benchmark.iloc[0]
    symbol=prices.columns[0]
    benchmark={'Date': prices.index[0],'Symbol':[symbol]}
    benchmark_order=pd.DataFrame(benchmark)
    benchmark_order['Order']='BUY'
    benchmark_order['Shares']=1000
    benchmark_order.set_index('Date', inplace=True)
    benchmark['daily_return'], benchmark_cr, benchmark_val=msc.compute_portvals(benchmark_order, sd, ed, start_val = 100000, commission=0, impact=impact)
    return benchmark_val

def get_BB(prices,sd, ed):
    prices_BB = prices.copy()
    t_SMA=50
    prices_BB['SMA']=pd.rolling_mean(prices_BB[symbol], window=t_SMA)
    t_std=30
    prices_BB['std']=pd.rolling_std(prices_BB[symbol], window=t_std)

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
    prices_BB['deliver_Shares'] = prices_BB['Order'].apply(deliver_shares)  
    prices_BB['deliver_Shares2']=prices_BB['deliver_Shares'].diff()
    prices_BB['Shares']=prices_BB['deliver_Shares2'].apply(shares)
    BB_Shares=prices_BB['Shares'].tolist()

    BB_Shares.pop(0)
    BB_Shares.append(0)
    prices_BB['Symbol']=symbol
    BB_order=pd.DataFrame(prices_BB, columns=['Symbol','Order'])
    BB_order['Shares']=np.asarray(BB_Shares)
    BB_order.index.name='Date'
    BB_order=BB_order[BB_order.Shares != 0]
    BB_shares_list=BB_order['Shares'].tolist()
    BB_shares_list[0]=1000
    BB_order['Shares']=BB_shares_list

    prices_BB['daily_return'], BB_cr, BB_val=msc.compute_portvals(BB_order, sd, ed, start_val = 100000, commission=0, impact=0.00)
    return BB_val

prices=get_prices(symbol, sd, ed, sv)
benchmark_val=get_benchmark(prices, sd, ed)
BB_val=get_BB(prices,sd, ed)
all_data=pd.DataFrame(benchmark_val, index=benchmark_val.index,columns=['benchmark'])
all_data['benchmark']=benchmark_val
all_data['BB']=BB_val
all_data['SL']=exp1_val
all_data = all_data/all_data.iloc[0]

benchmark_line=plt.plot(all_data['benchmark'], c='blue', label='Benchmark')
BB_line=plt.plot(all_data['BB'], c='black', label='BB')
SL_line=plt.plot(all_data['SL'], c='red', label='SL')
plt.title('Strategy Learning')
plt.xlabel('time')
plt.xticks(rotation=45)
plt.ylabel('Portfolio')
plt.legend()
plt.show()
plt.savefig('indicator vs SL')