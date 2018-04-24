#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 00:34:16 2018

@author: cxue1
"""

"""
A simple wrapper for linear regression.  (c) 2015 Tucker Balch
"""

import numpy as np
import RTLearner as rt
import DTLearner as dt
import BagLearner as bl
import LinRegLearner as lrl

#insaneLearner should contain 20 BagLearner instances 
#each instance is composed of 20 LinRegLearner instances
class InsaneLearner(object):
    def __init__(self, verbose = False):
        pass
    def author(self):
        return 'cxue34'
    
    def addEvidence(self, dataX, dataY):
        self.dataX=dataX
        self.dataY=dataY
        
    def query(self, test_dataX):
        all_Y=[]
        learner_bl=bl.BagLearner(learner = lrl.LinRegLearner, kwargs={}, bags = 20, boost = False, verbose = False)
        bag_learners=[]
        for i in range(0, 20):
            bag_learners.append(learner_bl)
        for lr in bag_learners:
            lr.addEvidence(self.dataX, self.dataY)
            trainY = lr.query(test_dataX)
            all_Y.append(trainY)
        predY=np.mean(np.array(all_Y), axis=0).tolist()
        return predY