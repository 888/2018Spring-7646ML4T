"""
A simple wrapper for linear regression.  (c) 2015 Tucker Balch
"""

import numpy as np
class DTLearner(object):
    def __init__(self, leaf_size = 1, verbose = False): 
        self.leaf_size = leaf_size
        self.verbose = verbose
    def author(self):
        return 'cxue34' 
    def build_tree(self, dataX, dataY):
        if dataX.shape[0] <= self.leaf_size or len(np.unique(dataX[:,-1]))==1:
            return np.array([-1, dataY.mean(), np.nan, np.nan])
        else:
            num_X=dataX.shape[1]
            corr_of_columns=[abs(np.corrcoef(dataX[:, i],dataY)[0,1]) for i in range(num_X)]
            best_column=np.nanargmax(corr_of_columns)
            SplitVal=np.median(dataX[:, best_column])                
            if (SplitVal == np.amax(dataX[:, best_column])) or (SplitVal == np.amin(dataX[:, best_column])):
                return np.array([-1, dataY.mean(), np.nan, np.nan])
            split_condition1=dataX[:, best_column]<=SplitVal
            split_condition2=dataX[:, best_column]>SplitVal  
            lefttree=self.build_tree(dataX[split_condition1], dataY[split_condition1])
            righttree=self.build_tree(dataX[split_condition2], dataY[split_condition2])
            lefttree_size = lefttree.ndim
            if lefttree_size > 1:
                self.root=np.array([best_column, SplitVal,1, lefttree.shape[0]+1])
            elif lefttree_size == 1:
                self.root = np.array([best_column, SplitVal,1, 2])
            return np.vstack((self.root, lefttree, righttree))
    def addEvidence(self,dataX,dataY):
        """
        @summary: Add training data to learner
        @param dataX: X values of data to add
        @param dataY: the Y training values
        """
        # slap on 1s column so linear regression finds a constant term
        self.tree = self.build_tree(dataX, dataY)
        if self.verbose == True:
            print(self.tree)        
    def query(self,dataX_test):
        """
        @summary: Estimate a set of test points given the model we built.
        @param points: should be a numpy array with each row corresponding to a specific query.
        @returns the estimated values according to the saved model.
        """
        trainY = []
        for row in dataX_test:
            i = 0
            while (i < self.tree.shape[0]):
                feature_ind = int(self.tree[i, 0])
                # Found leaf
                if feature_ind == -1:
                    break
                #Judge the data should go to left tree or right tree
                if row[feature_ind] > self.tree[i, 1]:
                    i += int(self.tree[i, 3])
                elif row[feature_ind] <= self.tree[i, 1]:
                    i += 1
            if feature_ind >= 0:
                trainY.append(np.nan)
            else:
                trainY.append(self.tree[i, 1])
        return trainY
if __name__=="__main__":
    print "the secret clue is 'zzyzx'"
