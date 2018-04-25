"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""

import datetime as dt
import numpy as np
import pandas as pd
import util as ut
import marketsimcode as msc
import QLearner as ql



class StrategyLearner(object):

    # constructor
    def __init__(self, verbose = False, impact=0.0):
        self.verbose = verbose
        self.impact = impact
        self.Qlearner = ql.QLearner(
            num_states = 10000,
            num_actions = 3,
            alpha = 0.2,
            gamma = 0.9,
            rar = 0.5,
            radr = 0.99,
            dyna = 0)
    def discritize_state(self, date, df):
        bb_s = pd.qcut((df['bb']),10, labels=False)
        sma_s = pd.qcut(df['sma'],10, labels=False)
        dsma_s = pd.qcut(df['dsma'],10, labels=False)
        std_s = pd.qcut(df['std'],10, labels=False)
        norm_s = pd.qcut(df['normalized'], 10, labels=False)
        return dsma_s.loc[date]*1000+bb_s.loc[date]*100+std_s.loc[date]*10+norm_s.loc[date]*1
    def deliver_shares(self,df):
        if df == 'BUY':
            val = 1
        elif df == 'SELL':
            val = -1
        else:
            val =0
        return val

    def shares(self,df):
        if df == 2 or df == -2:
            val = 2000
        else:
            val = 0
        return val
    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,12,31), \
        sv = 100000): 
        dates = pd.date_range(sd-dt.timedelta(100), ed)
        df = ut.get_data([symbol],dates)[symbol]
        normalized = df/df.ix[0] #df normalize
        t_sma=50
        sma = normalized.rolling(t_sma).mean()
        t_std=20
        std = normalized.rolling(t_std).std()
        dsma=normalized/sma-1
        bb=(normalized-(sma - std*2)) / (std*2)

        df = pd.DataFrame(df).assign(normalized = normalized).assign(sma = sma).assign(std=std).assign(dsma=dsma).assign(bb=bb)[sd:]

        #initial order
        df['Symbol']=symbol
        df['Order']='BUY'
        df_order=pd.DataFrame(df.iloc[0:1], columns=['Symbol','Order'])
        df_order['Shares']=1000
        impact=self.impact
        df['daily_return'], cr, df_val=msc.compute_portvals(df_order, sd, ed, start_val = 100000, commission=0.0, impact=impact)
        date_array=df.index

        #Q-learning setup
        epoch=0
        cr_old=cr
        cr_new=0.0001
        while (cr_new/cr_old<0.95 or cr_new/cr_old>1.05) and epoch<=15:
            epoch += 1
            cr_old=cr_new
            j=np.random.randint(len(date_array))
            date=date_array[j]
            s = self.discritize_state(date,df)
            a = self.Qlearner.querysetstate(s)
            i=0
            date=date_array[i+1]
            while i<len(date_array)-1:
                r=df.loc[date, 'daily_return']-impact
                s_prime=self.discritize_state(date,df)
                a = self.Qlearner.query(s_prime,r)
                if a==0:
                    df_order.loc[date, 'Order']='BUY'
                elif a==1:
                    df_order.loc[date, 'Order']='SELL'
                else:
                    df_order.loc[date, 'Order']='HOLD'
                i += 1
                date=date_array[i]
            #update df_order
            df_order_new=df_order[df_order['Order'] !='HOLD' ] 
            df_order_new['deliver_Shares'] = df_order_new['Order'].apply(self.deliver_shares)  
            df_order_new['deliver_Shares2']=df_order_new['deliver_Shares'].diff()
            df_order_new['Shares']=df_order_new['deliver_Shares2'].apply(self.shares)
            df_order_new = df_order_new.sort_index()
            shares_list=df_order_new['Shares'].tolist()
            shares_list.pop(0)
            shares_list.append(0)
            df_order_new=pd.DataFrame(df_order_new, columns=['Symbol','Order'])
            df_order_new['Symbol']=symbol
            df_order_new['Shares']=np.asarray(shares_list)
            df_order_new.index.name='Date'
            df_order_new=df_order_new[df_order_new['Shares'] != 0]
            df_shares_list=df_order_new['Shares'].tolist() 
            df_shares_list[0]=1000
            df_order_new['Shares']=df_shares_list
            df['daily_return'], cr_new, df_val=msc.compute_portvals(df_order_new, sd, ed, start_val = 100000, commission=0.0,impact=impact)
        
    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,12,31), \
        sv = 100000):

        dates = pd.date_range(sd-dt.timedelta(100), ed)
        df = ut.get_data([symbol],dates)[symbol]
        normalized = df/df.ix[0] #df normalize
        t_sma=50
        sma = normalized.rolling(t_sma).mean()
        t_std=20
        std = normalized.rolling(t_std).std()
        dsma=normalized/sma-1
        bb=(normalized-(sma - std*2)) / (std*2)

        df = pd.DataFrame(df).assign(normalized = normalized).assign(sma = sma).assign(std=std).assign(dsma=dsma).assign(bb=bb)[sd:]

        #setup states
        for index, row in df.iterrows():
            df.loc[index, 's']=self.discritize_state(index, df)
            s=int(df.loc[index, 's'])
            df.loc[index, 'a']=self.Qlearner.Q[s].argmax()                                       
            a=df.loc[index,'a']
            if a==0:
                df.loc[index, 'Order']='BUY'
            elif a==1:
                df.loc[index, 'Order']='SELL'
            else:
                df.loc[index, 'Order']='HOLD'

        #update df_order
        df_order_new=df[df['Order'] !='HOLD' ] 
        df_order_new['deliver_Shares'] = df_order_new['Order'].apply(self.deliver_shares)  
        df_order_new['deliver_Shares2']=df_order_new['deliver_Shares'].diff()
        df_order_new['Shares']=df_order_new['deliver_Shares2'].apply(self.shares)
        df_order_new = df_order_new.sort_index()
        shares_list=df_order_new['Shares'].tolist()
        shares_list.pop(0)
        shares_list.append(0)
        df_order_new=pd.DataFrame(df_order_new, columns=['Symbol','Order'])
        df_order_new['Symbol']=symbol
        df_order_new['Shares']=np.asarray(shares_list)
        df_order_new.index.name='Date'
        df_order_new=df_order_new[df_order_new['Shares'] != 0]
        df_shares_list=df_order_new['Shares'].tolist() 
        df_shares_list[0]=1000
        df_order_new['Shares']=df_shares_list
        #df['daily_return'], cr_new_t, df_val_t=msc.compute_portvals(df_order_new, sd, ed, start_val = 100000, commission=0.0,impact=impact)
        df_order_new['Shares']=df_order_new['Order'].apply(self.deliver_shares)*df_order_new['Shares']
        df['Shares']=df_order_new['Shares']
        trades=pd.DataFrame(df['Shares'].fillna(0))
        return trades
        


if __name__=="__main__":
    print ('strategy learner go')
