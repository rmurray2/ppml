# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 10:52:57 2015

@author: rm
"""

from __future__ import division
import xlrd
import datetime
import re
import numpy as np 
import urllib2
from sklearn.externals import joblib
from scipy import stats
import urllib
import json
from StringIO import StringIO
import csv
import os
from sklearn.externals import joblib
import shutil
 
class fred_data():
    def __init__(self, metric, dates, vals):
        self.dates = dates
        self.vals = vals
        self.metric = metric
        

book = xlrd.open_workbook('/home/ubuntu/dgrpred/U.S.DividendChampionsmr.xls')
sheet = book.sheet_by_index(0)
sheet2 = book.sheet_by_index(1)
divmonths = {}
threeavg = {}
frow = sheet.row_values(3, start_colx=60, end_colx=75)
fn_dict = {}
for i in range(6, 112):


    name = sheet.row_values(i, start_colx = 1, end_colx=2)[0]
    fn =  sheet.row_values(i, start_colx = 0, end_colx=1)[0]
    fn_dict[name] = fn
    row = sheet.row_values(i, start_colx=60, end_colx=75)
    row = np.array(row)
    row = row[row != 0]
#    print row, name, len(row)
    
    dm = sheet.row_values(i, start_colx=12, end_colx=13)[0]

    dm = datetime.datetime(*xlrd.xldate_as_tuple(dm, book.datemode)).month


    incount = 1
    d = {}
    for i in row[:-3]:
#        print row[incount:incount+3]
        d[str(int(frow[incount-1]))] = np.average(row[incount:incount+3])
#        print d
        incount += 1
    threeavg[name.lower()] = d    
    divmonths[name.lower()] = dm

    
for i in range(6, 256):

    name = sheet2.row_values(i, start_colx = 1, end_colx=2)[0]
    fn =  sheet2.row_values(i, start_colx = 0, end_colx=1)[0]
    fn_dict[name] = fn
    row = sheet2.row_values(i, start_colx=60, end_colx=75)
    row = np.array(row)
    row = row[row != 0]
#    print row, name, len(row)
    
    dm = sheet2.row_values(i, start_colx=12, end_colx=13)[0]

    dm = datetime.datetime(*xlrd.xldate_as_tuple(dm, book.datemode)).month
    
    incount = 1
    d = {}
    for i in row[:-3]:
#        print row[incount:incount+3]
        d[str(int(frow[incount-1]))] = np.average(row[incount:incount+3])
#        print d
        incount += 1
    threeavg[name.lower()] = d
    divmonths[name.lower()] = dm

#prime for day:
#    run pull_fred_daily.py (dump latest fred data) create fred persistence object
#    import get_upcoming_inc.py  and run get_upcoming_increases() #    modify home page to display what's available for now, and what's coming next week
#    for each ticker in next 30 days list: create csv-bsed persistence object with MR data (once, if directory already exists, skips it; some unecc repetition on ones that fail (e.g. missing data))  (future_prior)
#    for each ticker, fit all  existing data to find best features, save [features, fitted model] as model persistence objects (only done once after ticker appears in list)
#    check model persistence directory for old tickers, remove them
    
#on request:
#    load ticker content persistence object  (source: csvs)
#    load fred persistence object
#    construct data vector including inputted data
#    load fitted model, predict new value based on input!
    
#monthly: 
#   download morningstar data

joblib.dump(fn_dict, '/home/ubuntu/dgrpred/dump/fn_dict')
import pull_fred_daily
import get_upcoming_inc
import get_csv_data
import fit_model
import fit_new_data
#

pull_fred_daily.create_fred_objs()
#exit()
thirty_days, sixty_days = get_upcoming_inc.get_upcoming_increases() #get probable upcoming increaess
#
for ticker in sixty_days:
    print ticker, sixty_days[ticker]
    print 'starting get data'
    get_data = get_csv_data.gen_data_vector(ticker, threeavg, divmonths) #download MS data, generate data vectors
    print 'starting f'
    fit_model.fit(ticker)     #fit the models
#    print
#exit()

temp_persistence = [x[0] for x in os.walk('/home/ubuntu/dgrpred/dump/temp_persistence')][1:]


for d in temp_persistence:
    print d
    if d.split('/')[-1] not in sixty_days:
        print 'Deleting:', d
        shutil.rmtree(d) #remove folders not in next sixty days
