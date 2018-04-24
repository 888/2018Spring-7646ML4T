#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 23:46:22 2018

@author: cxue1
"""

"""
A simple wrapper for linear regression.  (c) 2015 Tucker Balch
"""
import RTLearner as rt
import DTLearner as dt
import LinRegLearner as lrl
import numpy as np
import random
class BagLearner(object):
    def __init__(self, learner = dt.DTLearner, kwargs={"argument1":1, "argument2":2}, bags = 20, boost = False, verbose = False):
        self.learner=learner
        self.kwargs = kwargs
        self.bags = bags
        self.boost = boost
        self.verbose = verbose
        self.learners = []
        for i in range(0, self.bags):
            self.learners.append(self.learner(**self.kwargs))
    def author(self):
        return 'cxue34'    
    def addEvidence(self, dataX, dataY):
        self.dataX=dataX
        self.dataY=dataY
    def query(self, test_dataX):
        all_Y=[]
        for lr in self.learners:
            data_size=self.dataX.shape[0]
            rand_ind=np.random.choice(data_size, data_size)
            rand_dataX=np.array([self.dataX.tolist()[i] for i in rand_ind])
            rand_dataY=np.array([self.dataY.tolist()[i] for i in rand_ind])
            lr.addEvidence(rand_dataX, rand_dataY)
            trainY = lr.query(test_dataX)
            all_Y.append(trainY)
        predY=np.mean(np.array(all_Y), axis=0).tolist()
        return predY
   


