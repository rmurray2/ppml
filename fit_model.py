# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 17:34:37 2015

@author: rm
"""
from __future__ import division
import numpy as np
import sklearn.metrics as metrics
from sklearn import feature_selection
from sklearn import linear_model as lm
from sklearn import preprocessing
from sklearn import decomposition
from sklearn.externals import joblib
from sklearn.svm import SVR
import os

def MAD(target, prediction):
    ad = np.abs(target-prediction)
    return np.mean(ad)
    
MAD_loss = metrics.make_scorer(MAD, greater_is_better=False)     

class RFE_CV():
    def __init__(self, step):
        self.step = step
#        self.estimator =  SVC(kernel="linear", C=1)
#        self.estimator = SVR(kernel="linear")#lm.Lasso()#
        self.estimator = lm.BayesianRidge()

        pass
    
    def fit_transform(self, x, y):
        
        
        kb = feature_selection.SelectKBest(feature_selection.f_regression, k=500)
        x_norm_pre  = kb.fit_transform(x, y)        
        idx = np.arange(0, x.shape[1])
        features_to_keep = idx[kb.get_support() == True] #indexpositionsof chosen feats

        rfecv = feature_selection.RFECV(estimator=self.estimator, cv=8,  scoring=MAD_loss,) 
        best_feature_values = rfecv.fit_transform(x_norm_pre, y) #pass the feats to RFECV to pik best one
        
        kept_indices_final= features_to_keep[rfecv.support_ == True] #chooe index poitions frm fist pass that also made t rhough csecond pass 
        final_features = np.zeros(x.shape[1], dtype=np.bool) #arr of Falses
        final_features[kept_indices_final] = np.True_     #change finally choen feats  Trues
        self.features_to_keep = final_features
        return best_feature_values
        
    def get_support(self):        
        return self.features_to_keep
        
    def transform(self):
        pass
    
    def get_params(self):
        pass    
     
def fit(ticker):

    if not os.path.isdir('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker): #don't fit model if the data's not there
        return None
    if os.path.isfile('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_features_kept'): #skip if it s already been fitted
        print 'none'
        return None
    print 'went in'
    x  = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_x', delimiter=',')
    y  = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_y', delimiter=',')
    scale = preprocessing.StandardScaler()
    
    x_norm = scale.fit_transform(x)
    
    rfecv = RFE_CV(1)#feature_selection.RFECV(estimator=estimator, scoring=RMSE_loss,)
    g = rfecv.fit_transform(x_norm[:-1], y[:-1]) #first fit all but last
    if g == None:
        return None
   
    idx = np.arange(0, x.shape[1])
    features_to_keep = idx[rfecv.get_support() == True]    

    x_norm_fs = x_norm[:,features_to_keep]
    
    kern=decomposition.KernelPCA(kernel='sigmoid')
    
    try:
        x_norm_fs_fe = kern.fit_transform(x_norm_fs)
    except:
        return None
    
    model = SVR(kernel="linear")

    model.fit(x_norm_fs_fe[:-1], y[:-1])
    pred = model.predict(x_norm_fs_fe[-1])    
    #actual, prediction
    test_perf_obj = []
    test_perf_obj.append(y[-1])
    try:
        test_perf_obj.append(pred[0])
    except:
        test_perf_obj.append(pred)
    
    test_perf_obj = np.array(test_perf_obj)
    np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_test_perf', test_perf_obj, delimiter = ',')
    
    #######################################################now FS on all data 
#    
    x_norm = scale.fit_transform(x)
#    
    rfecv = RFE_CV(1)#feature_selection.RFECV(estimator=estimator, scoring=RMSE_loss,)
    g = rfecv.fit_transform(x_norm, y) #first fit all but last
    if g == None:
        return None
#   
    idx = np.arange(0, x.shape[1])
    features_to_keep = idx[rfecv.get_support() == True]    
#
#    x_norm_fs = x_norm[:,features_to_keep]
#    
#    kern=decomposition.KernelPCA(kernel='sigmoid')
#    
#    try:
#        x_norm_fs_fe = kern.fit_transform(x_norm_fs)
#    except:
#        return None
#    
#    model = SVR(kernel="linear")
#
#    model.fit(x_norm_fs_fe, y)
    
#    joblib.dump(model, '/home/rm/ppml/dump/temp_persistence/'+ticker+'/'+ticker+'_fitted_model')
    joblib.dump(features_to_keep, '/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_features_kept')
    
