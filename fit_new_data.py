# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 18:07:45 2015

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
import itertools
import datetime
from scipy import stats

def MAD(target, prediction):
    ad = np.abs(target-prediction)
    return np.mean(ad)
    
MAD_loss = metrics.make_scorer(MAD, greater_is_better=False)     

def gendata(values):
    
    retvector = []

    for x, y in itertools.combinations(values, 2):
        if x == 0 or y == 0:

            retvector.append(0)

            continue

        t = x/y
        
        retvector.append(t)
#        retvector.append(tt)
    retvector = np.array(retvector, np.float32)
    return retvector
    
    
def calc_vals(start, end, dates, vals):
    startindx = dates.index(start)
    endindx = dates.index(end)
    
    poi = []
    for i in range(startindx, endindx+1):
#        print vals[i]
        poi.append(vals[i])
    vals = np.array(poi)
    mean = np.mean(poi)

    slope, intercept, r_value, p_value, std_err = stats.linregress(range(1, len(vals)+1), vals)
    
    return mean, slope
    
    
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
    
def fit(ticker, rev_future, eps_future, roe_future, netmarg_future, dtoe_future):
    
    new_data_vector = []
    mr_div = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_mr_div', delimiter=',')
    mr_price = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_mr_price', delimiter=',')
    prior_data = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_future_prior', delimiter=',')
    fredobjs = joblib.load('/home/ubuntu/dgrpred/dump/fred_obj_temp_dump')
#    fitted_model = joblib.load('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_fitted_model')
    features_to_keep = joblib.load('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_features_kept')
    x_loaded  = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_x', delimiter=',')
    y_loaded  = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_y', delimiter=',')
    
    cog =  round((rev_future/roe_future)*roe_future, 5)

    fg = eps_future - mr_div - cog

    sc = fg/mr_price    
    pred = sc + rev_future
    
    ############################################load new data
    new_data_vector.append(cog)
    new_data_vector.append(sc)
    new_data_vector.append(fg)
    new_data_vector.append(pred)
    new_data_vector.append(roe_future)
    new_data_vector.append(rev_future)
    new_data_vector.append(netmarg_future)
    new_data_vector.append(eps_future)
    new_data_vector.append(dtoe_future)

    
    
    for i in prior_data:
        new_data_vector.append(i)
#    print len(new_data_vector), 'first'
    
    nd = gendata(new_data_vector)
    for i in nd:
        new_data_vector.append(float(i))
        
#    print len(new_data_vector), 'beforefred'
    for i in fredobjs:
    
        q = datetime.datetime.strptime(i.dates[-1], "%Y-%m-%d") #go back one year from latest data point
    
        last_year_from_last_date = q.replace(year=q.year-1)
    
        last_year_from_last_date = datetime.datetime.strftime(last_year_from_last_date, "%Y-%m-%d")
        mean, slope = calc_vals(last_year_from_last_date, i.dates[-1], i.dates, i.vals)

        new_data_vector.append(mean)
        new_data_vector.append(slope)
    
    nd = gendata(new_data_vector)
    
    for i in nd:
        new_data_vector.append(float(i))
    
    x = np.array(new_data_vector, dtype=np.float32)
    x = np.asmatrix(x)
    
    ########################################################################################
    x_complete = np.concatenate((x_loaded, x)) #concat old data with new
    
    scale = preprocessing.StandardScaler()
#    print x_complete
    x_norm = scale.fit_transform(x_complete)
    
#    print x_norm
    x_norm_fs = x_norm[:,features_to_keep] #use previously determined features
#    print x_norm_fs.shape
#    print x_norm_fs
    kern=decomposition.KernelPCA(kernel='sigmoid')
    
    try:
        x_norm_fs_fe = kern.fit_transform(x_norm_fs)
    except:
        return None
        
    model = SVR(kernel="linear")

    model.fit(x_norm_fs_fe[:-1], y_loaded)
    pred = model.predict(x_norm_fs_fe[-1]) 
    return pred

#    #actual, prediction
#    test_perf_obj = []
#    test_perf_obj.append(y[-1])
#    try:
#        test_perf_obj.append(pred[0])
#    except:
#        test_perf_obj.append(pred)
#    
#    test_perf_obj = np.array(test_perf_obj)
#    np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_test_perf', test_perf_obj, delimiter = ',')
#    
#    #######################################################now fit all data
#    
#    x_norm = scale.fit_transform(x)
#    
#    rfecv = RFE_CV(1)#feature_selection.RFECV(estimator=estimator, scoring=RMSE_loss,)
#    g = rfecv.fit_transform(x_norm, y) #first fit all but last
#    if g == None:
#        return None
#   
#    idx = np.arange(0, x.shape[1])
#    features_to_keep = idx[rfecv.get_support() == True]    
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
#    
#    joblib.dump(model, '/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_fitted_model')
#    
#    
