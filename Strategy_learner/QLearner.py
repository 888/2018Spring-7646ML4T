"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):

    def author(self):
        return 'cxue34'
    
    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.s = 0
        self.a = 0
        self.num_states=num_states
        self.alpha=alpha
        self.gamma=gamma
        self.rar=rar
        self.radr=radr
        self.dyna=dyna
        
        self.Q=np.zeros((self.num_states,self.num_actions))
        self.R=np.zeros((self.num_states,self.num_actions))
        self.Tc=np.zeros((self.num_states, self.num_actions, self.num_states))
        self.T=np.zeros((self.num_states, self.num_actions, self.num_states))

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        action = rand.randint(0, self.num_actions-1)
        if self.verbose: print ("s =", s,"a =",action)
        return action

    
    
    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """

        pre_s=self.s
        pre_a=self.a
        new_s=s_prime
        num_actions=self.num_actions 
        rar=self.rar
        radr =self.radr
        alpha=self.alpha
        gamma=self.gamma
        dyna=self.dyna
        reward=r      
        num_states=self.num_states
        def Q_action(Q, s):
            actions=Q[s]
            best_action=np.argmax(actions)
            return best_action
        if rar > rand.random():
            action=rand.randint(0,num_actions-1)
        else:
            action=Q_action(self.Q,new_s)
        pre_val=self.Q[pre_s][pre_a]
        new_val=self.Q[new_s][action]
        self.Q[pre_s][pre_a]=(1.0-alpha)*pre_val+alpha*(reward+gamma*new_val)
            
        if dyna > 0:
            self.Tc[pre_s][pre_a][new_s]=self.Tc[pre_s][pre_a][new_s]+1
            self.R[pre_s][pre_a]=(1.0-alpha)*self.R[pre_s][pre_a]+alpha*(reward)
            self.T[pre_s][action]=self.Tc[pre_s][action]/sum(self.Tc[pre_s][action][:])
            np_T=tuple(self.T)
            for i in range(dyna):
                a=rand.randint(0,num_actions-1)
                s=rand.randint(0,num_states-1)
                r=self.R[s][a]
                s_i=np_T[s][a].argmax()    
                self.Q[s][a]=(1.0-alpha)*self.Q[s][a]+alpha*(r+gamma*self.Q[s_i][Q_action(self.Q,s_i)])
   
        self.s=s_prime
        self.a=action
        self.rar=rar*radr

        if self.verbose: print ("s =", s_prime,"a =",action,"r =",r)
        return action


if __name__=="__main__":
    print ("Remember Q from Star Trek? Well, this isn't him")
