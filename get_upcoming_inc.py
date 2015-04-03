# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 18:35:29 2015

@author: rm
"""
import xlrd
import datetime 
from sklearn.externals import joblib

def get_upcoming_increases():
    
    ##################################read xls file
    book = xlrd.open_workbook('/home/ubuntu/dgrpred/U.S.DividendChampionsmr.xls')
    sheet = book.sheet_by_index(0)
    sheet2 = book.sheet_by_index(1)
    ex_date_dict = {}

    for i in range(6, 112):
        ex_date = sheet.row_values(i, start_colx=12, end_colx=13)[0]
        ex_date = datetime.datetime(*xlrd.xldate_as_tuple(ex_date, book.datemode))
    
        name = sheet.row_values(i, start_colx = 1, end_colx=2)[0]
        ex_date_dict[name.lower()] = ex_date
    
    for i in range(6, 256): 
    
        name = sheet2.row_values(i, start_colx = 1, end_colx=2)[0]
        
     
        ex_date = sheet2.row_values(i, start_colx=12, end_colx=13)[0]
        ex_date = datetime.datetime(*xlrd.xldate_as_tuple(ex_date, book.datemode))
        ex_date_dict[name.lower()] = ex_date
    ######################################################################################################
    ##################################estimate next increase date, 30 days and 60 days into future, return dictionaries
    now = datetime.datetime.now()
    this_year = now.year
    ex_dec_diff = joblib.load('/home/ubuntu/dgrpred/dump/ex_dec_diff') #the difference between declaration/ex date STATIC
        
    upcoming_one_month = {}
    upcoming_two_month = {}
    for i in ex_date_dict: #for each ticker symbol

        if ex_date_dict[i].year == this_year or i not in ex_dec_diff: # if the MR increase was last year
            continue

        ex_date_dict[i]= ex_date_dict[i].replace(year=this_year)
    
        now = datetime.datetime.now()
        one_month_ahead= now + datetime.timedelta(days = 30)
        two_months_ahead= now + datetime.timedelta(days = 60)
	one_week_ago = now - datetime.timedelta(days = 7)
        est = abs(ex_dec_diff[i][0])+ abs(ex_dec_diff[i][1])   #average +  std + 7 days
        
        announcement_est = ex_date_dict[i] - datetime.timedelta(days = est)
	#announcement_est -= datetime.timedelta(days = 5)
        if (announcement_est <= one_month_ahead) and (announcement_est > one_week_ago ):
            upcoming_one_month[i] = announcement_est   
           
#           print announcement_est, i, ex_dec_diff[i][0], ex_dec_diff[i][1]
    #        print
    
        if (announcement_est <= two_months_ahead) and (announcement_est > one_week_ago ):
            upcoming_two_month[i] = announcement_est
#            print '60 days', announcement_est, i, ex_dec_diff[i][0], ex_dec_diff[i][1]
    
    joblib.dump(upcoming_one_month, '/home/ubuntu/dgrpred/dump/temp_persistence/upcoming_one_month')
    joblib.dump(upcoming_two_month, '/home/ubuntu/dgrpred/dump/temp_persistence/upcoming_two_month')
    return upcoming_one_month, upcoming_two_month




        
