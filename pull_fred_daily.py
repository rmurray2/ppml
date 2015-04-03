# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 18:24:46 2015

@author: rm
"""

import urllib
from sklearn.externals import joblib
import json 
import copy

def pullfred(start, series):
    print start
    api_key = ''
    q =urllib.urlopen('http://api.stlouisfed.org/fred/series/observations?series_id='+series+'&api_key='+api_key+''&file_type=json&frequency=m&units=pc1&observation_start='+str(start)+'-'+'01'+'-01&observation_end=9999-12-31').read()
    text = json.loads(q) 
#    print text
    vals = []
#    print text
    dates = []
    for i in text['observations']:
        try:
            vals.append(float(i['value']))
            dates.append(i['date'])
        except:
            pass
    
    return dates, vals
    
class fred_data():
    def __init__(self, metric, dates, vals):
        self.dates = dates
        self.vals = vals
        self.metric = metric
        


def create_fred_objs():
    fseries = ['NAPMII','CUUR0000SA0L2', 'IPFINAL','CUUR0000SAD','HOUSTNE',
               'MHHNGSP','WJFUELUSGULF','CES1021000001','PRRESCONS','PNRESCONS', 
               'DDURRG3M086SBEA', 'DSERRG3M086SBEA', 'IPNCONGD', 'IPCONGD', 'HOUSTMW', 'USGOOD', 
               'ACOGNO', 'PPICMM', 'NONREVSL', 'IPFUELS', 'IPMAT', 'BAAFFM', 'M2REAL', 'IPDCONGD',
               'IPBUSEQ', 'USTRADE', 'PPIITM', 'CES3000000008', 'BUSINV', 'CPIAUCSL','NAPMNOI','MCOILWTICO',
               'INDPRO','HOUST','UNRATE','DGORDER','PPIFGS','CPIMEDSL','RSAFS','CPIAPPSL','CPITRNSL','IPMANSICS',
               'USCONS','NAPMEI','NAPMPRI','NAPMPI','NAPMSDI','PPICRM']
    fredobjs = []
    for q in fseries:
        print q, 'this'
        dates, vals= pullfred(2003, q) #go back to 2003, ending with MR data
        obj = fred_data(q, dates, vals)
        fredobjs.append(copy.deepcopy(obj))
            
    joblib.dump(fredobjs, '/home/ubuntu/dgrpred/dump/fred_obj_temp_dump')

