# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 19:10:38 2015

@author: rm
"""
from __future__ import division
import os
import csv
from StringIO import StringIO
import calendar
import datetime
import matplotlib.finance as mf
import urllib2
import copy 
import itertools
from scipy import stats
import numpy as np
from sklearn.externals import joblib
import shutil

class fred_data():
    def __init__(self, metric, dates, vals):
        self.dates = dates
        self.vals = vals
        self.metric = metric

def mr_stock_price(ticker):
    now = datetime.datetime.now()
    earlier =  now - datetime.timedelta(days = 4)
    price = mf.fetch_historical_yahoo(ticker, (earlier.year, earlier.month, earlier.day), (now.year, now.month, now.day), dividends=False)
     
    for r in price:
        r = r.split(',')
        try:
            float(r[-1])
            mr_price= float(r[-1].strip())
            break
#            shareprices.append(float(r[-1].strip()))
        except:
            continue    
    return mr_price
        
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
    
def gendata(values, labels):
    retlabels = []
    
    retvector = []

    for x, y in itertools.combinations(values, 2):
        if x == 0 or y == 0:

            retvector.append(0)
            
#            retvector.append(0)
            continue
#        print x, y
        t = x/y
        retlabels.append(str(labels[values.index(x)]) +'/'+ str(labels[values.index(y)]))
        
#        tt = y/x
#        retlabels.append(str(labels[values.index(y)]) +'/'+ str(labels[values.index(x)]))
        
        retvector.append(t)
#        retvector.append(tt)
    retvector = np.array(retvector, np.float32)
    return retvector, retlabels
    
def readcsv(ticker, new):
    content = {}
    if new  == False:
        q = open('/home/ubuntu/dgrpred/old_csv/'+ticker, 'r').read().split('\n')
    else:
        q = open(ticker, 'r').read().split('\n')
    for i in q:
        i = i.split(',')
        if i[0] == 'Profitability':            
            years = i[1:-1]
    rev, opinc, netinc, eps = False, False, False, False
    for i in q:

        if '"' in i:
            line = []
            data = StringIO(i) 
            reader = csv.reader(data, delimiter=',') 
            for row in reader:
                for r in row:
                    line.append(r.replace(',', ''))
            
        else:
            line = i.split(',')  
            
        if 'Revenue %' in line:
            rev = True
        if 'Operating Income %' in line:
            rev = False
            opinc = True
        if 'Net Income %' in line:
            opinc = False
            netinc = True
        if 'EPS %' in line:
            netinc = False
            eps = True
        if 'Key Ratios -> Cash Flow' in line:
            eps = False
            
        if len(line) >5 and line[0] != '':
            if rev == True:
                content['rev-'+line[0]] = {}
            else:
                if opinc == True:
                    content['opinc-'+line[0]] = {}
                else:
                    if netinc == True:
                        content['netinc-'+line[0]] = {}
                    else:
                        if eps == True:
                            content['eps-'+line[0]] = {}
                        else:
                            content[line[0]] = {}
                    
            count =1
            for j in years:
                if rev == True:
                    content['rev-'+line[0]][j] = line[count]

                else:
                    if opinc == True:
                        content['opinc-'+line[0]][j] = line[count]
                    else:
                        if netinc == True:
                            content['netinc-'+line[0]][j] = line[count]
                        else:
                            if eps == True:
                                content['eps-'+line[0]][j] = line[count]
                            else:
                                content[line[0]][j] = line[count]
                count += 1     
                
    return content
    
def calc_delta(x):
    xchange = [] #
    count =0
    for i in x[1:]:
        t = round(((float(i)-float(x[count]))/float(x[count]))*100, 5)

        count += 1
        xchange.append(t)
    return xchange


def gen_data_vector(ticker, threeavg, divmonths):
    try:
        if os.path.isdir('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker):# if it's already there, skip it
            return None

        os.mkdir('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker)
        fredobjs = joblib.load('/home/ubuntu/dgrpred/dump/fred_obj_temp_dump')
    
        divmonth = divmonths[ticker]
        
        print '*********************'
        print ticker, divmonth
        if divmonth < 10:
            divmonth = '0'+str(divmonth)
        else:
            divmonth = str(divmonth)
                
        oldcsvs = os.listdir('/home/ubuntu/dgrpred/old_csv/')
        olddata = {}
        
        for i in oldcsvs:
        #    print i
            olddata[i.split('.')[0]] = readcsv(i, False)
        
        url = 'http://financials.morningstar.com/ajax/exportKR2CSV.html?&callback=?&t='+ticker.upper()+'&region=usa&culture=en-US&cur=USD&order=asc'
        
        opener = urllib2.build_opener()
        
        f = opener.open(url)
        data = f.read()
        with open('/home/ubuntu/dgrpred/new_csv/'+ticker.replace('/', '').upper()+'.csv', 'wb') as code:
            code.write(data)
        
        content = readcsv('/home/ubuntu/dgrpred/new_csv/'+ticker.upper()+'.csv', True)
            
        ##################fill in downloaded data with old data if new data is missing
        for i in content:
            for j in content[i]:
                if content[i][j] == '' or content[i][j] == '--':
                    try:
                        content[i][j] = olddata[ticker.upper()][i][j]
                    except:
                        pass
        #    for i in olddata[ticker.upper()]:
        #        print i, olddata[ticker.upper()][i]
        #        print
        #    exit()
        years = []
        fye = []
        for i in content['Profitability']:
            years.append(int(i.split('-')[0]))
            fye.append(int(i.split('-')[1]))
            
        years.sort()
        
        fye = list(set(fye))[0]
        if fye < 10:
            fye = '0'+str(fye)
        else:
            fye = str(fye)
    
        count = 0
        content_cleaned = copy.deepcopy(content)
        
        for measure in content:
        #            print measure
            for year in content[measure]:
        
                if content[measure][year] == '':
        
                    del content_cleaned[measure]
                    break
                else:
                    try:
                        content[measure][year] = float(content[measure][year])
                    except:
        
                        del content_cleaned[measure]
                        break
        print '---'
        
        #        for measure in content_cleaned: 
        #            print measure
        #            for year in content_cleaned[measure]:
        #                print content_cleaned[measure][year]
                
        
        content = content_cleaned
        #        exit()
        
        content['shareprices'] = {}
        count = 0
        for x in range(int(years[0]), int(years[-1])+1):
            dd = 8
            while calendar.weekday(x, 8, dd) >= 5:
                dd +=1
            price = mf.fetch_historical_yahoo(ticker, (x, 8, dd), (x, 8, dd), dividends=False)
            
            for r in price:
                r = r.split(',')
                try:
                    float(r[-1])
                    content['shareprices'][str(years[count])+'-'+str(fye)] = float(r[-1].strip())
        #            shareprices.append(float(r[-1].strip()))
                except:
                    continue
            count += 1
            
        
        content['divyoy'] = {}
        divs = []
        for i in years:
            divs.append(content['Dividends USD'][str(i)+'-'+str(fye)])
        
        divdelta= calc_delta(divs)
        count = 1
        
        for i in divdelta:
            content['divyoy'][str(years[count])+'-'+str(fye)] = i
            count += 1
        
        for i in content:
            for j in content[i]:
                if content[i][j] == '':
                    print i, j
        
        cogs = [] # 
        cogs_prior = []
        count = 1
        
        for i in years[1:]:
            print i
            eps_prior = float(content['Earnings Per Share USD'][str(years[count-1])+'-'+fye])
        #        print content['rev-Year over Year'][str(years[count-1])+'-'+fye]
            rev_prior = float(content['rev-Year over Year'][str(years[count-1])+'-'+fye])
            roe_prior = float(content['Return on Equity %'][str(years[count-1])+'-'+fye])
            cog =  round((rev_prior/roe_prior)*eps_prior, 5)
            cogs_prior.append(cog) 
        
            eps = float(content['Earnings Per Share USD'][str(years[count])+'-'+fye])
            rev = float(content['rev-Year over Year'][str(years[count])+'-'+fye])
            roe = float(content['Return on Equity %'][str(years[count])+'-'+fye])    
            cog =  round((rev/roe)*eps, 5)
            cogs.append(cog) 
        #    
            count += 1
        
        count = 1
        fgs = [] # 
        fgs_prior = []
        for i in cogs_prior:
            fg = round((float(content['Earnings Per Share USD'][str(years[count-1])+'-'+fye]) - float(content['Dividends USD'][str(years[count-1])+'-'+fye]) - i), 5)
            fgs_prior.append(fg)
            
            fg = round((float(content['Earnings Per Share USD'][str(years[count])+'-'+fye]) - float(content['Dividends USD'][str(years[count-1])+'-'+fye]) - cogs[count-1]), 5)
            fgs.append(fg)
            count += 1
            
        sc = [] # 
        sc_prior = []
        count = 0
        print content['shareprices']
        for i in fgs:
            sharep =  float(content['shareprices'][str(years[count])+'-'+str(fye)])
            
            t = round((i/sharep)*100, 5)
            sc.append(t)
            
            t = round((fgs_prior[count]/sharep)*100, 5)
            sc_prior.append(t)
            count += 1  
        
        pred = [] #
        pred_prior = []
        count = 1
        for i in sc:
            rev = float(content['rev-Year over Year'][str(years[count])+'-'+fye])
            t = i + rev
            pred.append(t)
            
            rev_prior = float(content['rev-Year over Year'][str(years[count-1])+'-'+fye])
            t = sc_prior[count-1] + rev_prior
            print sc_prior[count-1], rev_prior
            pred_prior.append(t)
            count += 1
        
        x = []
        y = []
        count = 1
        #        feature_labels = ['eps_prior', 'eps_future', 'payoutratio_prior', 'divs_prior', 'cogs_prior', 'cogs_future', 'sharechange_prior', 'sharechange_future', 'funding_gap_prior', 'funding_gap_future', 'prediction_prior', 'prediction_future', 'revYOY_prior', 'revYOY_future', 'roe_prior', 'roe_future', 'shareprice_prior', 'three_yr_trailing_dgr', 'NAPMIImean', 'NAPMIIslope', 'CUUR0000SA0L2mean', 'CUUR0000SA0L2slope', 'IPFINALmean', 'IPFINALslope', 'CUUR0000SADmean', 'CUUR0000SADslope', 'HOUSTNEmean', 'HOUSTNEslope', 'MHHNGSPmean', 'MHHNGSPslope', 'WJFUELUSGULFmean', 'WJFUELUSGULFslope', 'CES1021000001mean', 'CES1021000001slope', 'PRRESCONSmean', 'PRRESCONSslope', 'PNRESCONSmean', 'PNRESCONSslope', 'DDURRG3M086SBEAmean', 'DDURRG3M086SBEAslope', 'DSERRG3M086SBEAmean', 'DSERRG3M086SBEAslope', 'IPNCONGDmean', 'IPNCONGDslope', 'IPCONGDmean', 'IPCONGDslope', 'HOUSTMWmean', 'HOUSTMWslope', 'USGOODmean', 'USGOODslope', 'ACOGNOmean', 'ACOGNOslope', 'PPICMMmean', 'PPICMMslope', 'NONREVSLmean', 'NONREVSLslope', 'IPFUELSmean', 'IPFUELSslope', 'IPMATmean', 'IPMATslope', 'BAAFFMmean', 'BAAFFMslope', 'M2REALmean', 'M2REALslope', 'IPDCONGDmean', 'IPDCONGDslope', 'IPBUSEQmean', 'IPBUSEQslope', 'USTRADEmean', 'USTRADEslope', 'PPIITMmean', 'PPIITMslope', 'CES3000000008mean', 'CES3000000008slope', 'BUSINVmean', 'BUSINVslope', 'CPIAUCSLmean', 'CPIAUCSLslope', 'NAPMNOImean', 'NAPMNOIslope', 'MCOILWTICOmean', 'MCOILWTICOslope', 'INDPROmean', 'INDPROslope', 'HOUSTmean', 'HOUSTslope', 'UNRATEmean', 'UNRATEslope', 'DGORDERmean', 'DGORDERslope', 'PPIFGSmean', 'PPIFGSslope', 'CPIMEDSLmean', 'CPIMEDSLslope', 'RSAFSmean', 'RSAFSslope', 'CPIAPPSLmean', 'CPIAPPSLslope', 'CPITRNSLmean', 'CPITRNSLslope', 'IPMANSICSmean', 'IPMANSICSslope', 'USCONSmean', 'USCONSslope', 'NAPMEImean', 'NAPMEIslope', 'NAPMPRImean', 'NAPMPRIslope', 'NAPMPImean', 'NAPMPIslope', 'NAPMSDImean', 'NAPMSDIslope', 'PPICRMmean', 'PPICRMslope']
        fred_labels = ['NAPMIImean', 'NAPMIIslope', 'CUUR0000SA0L2mean', 'CUUR0000SA0L2slope', 'IPFINALmean', 'IPFINALslope', 'CUUR0000SADmean', 'CUUR0000SADslope', 'HOUSTNEmean', 'HOUSTNEslope', 'MHHNGSPmean', 'MHHNGSPslope', 'WJFUELUSGULFmean', 'WJFUELUSGULFslope', 'CES1021000001mean', 'CES1021000001slope', 'PRRESCONSmean', 'PRRESCONSslope', 'PNRESCONSmean', 'PNRESCONSslope', 'DDURRG3M086SBEAmean', 'DDURRG3M086SBEAslope', 'DSERRG3M086SBEAmean', 'DSERRG3M086SBEAslope', 'IPNCONGDmean', 'IPNCONGDslope', 'IPCONGDmean', 'IPCONGDslope', 'HOUSTMWmean', 'HOUSTMWslope', 'USGOODmean', 'USGOODslope', 'ACOGNOmean', 'ACOGNOslope', 'PPICMMmean', 'PPICMMslope', 'NONREVSLmean', 'NONREVSLslope', 'IPFUELSmean', 'IPFUELSslope', 'IPMATmean', 'IPMATslope', 'BAAFFMmean', 'BAAFFMslope', 'M2REALmean', 'M2REALslope', 'IPDCONGDmean', 'IPDCONGDslope', 'IPBUSEQmean', 'IPBUSEQslope', 'USTRADEmean', 'USTRADEslope', 'PPIITMmean', 'PPIITMslope', 'CES3000000008mean', 'CES3000000008slope', 'BUSINVmean', 'BUSINVslope', 'CPIAUCSLmean', 'CPIAUCSLslope', 'NAPMNOImean', 'NAPMNOIslope', 'MCOILWTICOmean', 'MCOILWTICOslope', 'INDPROmean', 'INDPROslope', 'HOUSTmean', 'HOUSTslope', 'UNRATEmean', 'UNRATEslope', 'DGORDERmean', 'DGORDERslope', 'PPIFGSmean', 'PPIFGSslope', 'CPIMEDSLmean', 'CPIMEDSLslope', 'RSAFSmean', 'RSAFSslope', 'CPIAPPSLmean', 'CPIAPPSLslope', 'CPITRNSLmean', 'CPITRNSLslope', 'IPMANSICSmean', 'IPMANSICSslope', 'USCONSmean', 'USCONSslope', 'NAPMEImean', 'NAPMEIslope', 'NAPMPRImean', 'NAPMPRIslope', 'NAPMPImean', 'NAPMPIslope', 'NAPMSDImean', 'NAPMSDIslope', 'PPICRMmean', 'PPICRMslope']
        #        feature_labels = ['cog', 'cog_prior', 'sc', 'sc_prior', 'funding gap', 'funding gap_prior', 'pred', 'pred_prior', 'rev', 'rev_prior', 'CPIAUCSL-mean','CPIAUCSL-slope','UNRATE-mean','UNRATE-slope','MCOILWTICO-mean','MCOILWTICO-slope','INDPRO-mean','INDPRO-slope', 'HOUST-mean','HOUST-slope', 'NAPMNOI-mean','NAPMNOI-slope', 'DGORDER-mean','DGORDER-slope', 'PPIFGS-mean','PPIFGS-slope', 'CPIMEDSL-mean','CPIMEDSL-slope', 'RSAFS-mean','RSAFS-slope', 'CPIAPPSL-mean','CPIAPPSL-slope', 'CPITRNSL-mean','CPITRNSL-slope', 'IPMANSICS-mean','IPMANSICS-slope', 'USCONS-mean','USCONS-slope', 'NAPMEI-mean','NAPMEI-slope', 'NAPMPRI-mean','NAPMPRI-slope', 'NAPMPI-mean','NAPMPI-slope', 'NAPMSDI-mean','NAPMSDI-slope', 'PPICRM-mean', 'PPICRM-slope']
        #        fseries = ['NAPM', 'CPIAUCSL','UNRATE','MCOILWTICO','INDPRO','HOUST','NAPMNOI','DGORDER','PPIFGS','CPIMEDSL','RSAFS','CPIAPPSL','CPITRNSL','IPMANSICS','USCONS','NAPMEI','NAPMPRI','NAPMPI','NAPMSDI','PPICRM']
        
        labelsSaved=  False
        for i in years[1:]:
            feature_labels =[]
            temp = []
                         
             ############################################# future (aka future prior data)
            temp.append(float(cogs[count-1]))
            feature_labels.append('cogs_future')
            
            temp.append(float(float(sc[count-1])))
            feature_labels.append('sc_future')
            
            temp.append(float(fgs[count-1]))
            feature_labels.append('fg_future')
                    
            temp.append(float(pred[count-1]))
            feature_labels.append('pred_future')
            
            temp.append(float(content['Return on Equity %'][str(years[count])+'-'+fye]))
            feature_labels.append('roe_future')
            
            rev = float(content['rev-Year over Year'][str(years[count])+'-'+fye])
            temp.append(rev)
            feature_labels.append('revyoy_future')
                   
            netmarg = float(content['Net Margin %'][str(years[count])+'-'+fye])
            temp.append(netmarg)
            feature_labels.append('netmarg_future')
                    
            temp.append(float(content['Earnings Per Share USD'][str(years[count])+'-'+fye]))
            feature_labels.append('eps_future')
        
            temp.append(float(content['Debt/Equity'][str(years[count])+'-'+str(fye)])) #d-to-e
            feature_labels.append('dtoe_future')
            
            if i == years[-1]:
                
                future_prior_data = copy.deepcopy(temp)
                print len(future_prior_data), '********'
                
                payout_future = float(content['Payout Ratio %'][str(years[count])+'-'+fye])
                future_prior_data.append(payout_future)
                
                threeyravg = calc_delta(divs)
                mr_threeyravg = sum(threeyravg[-3:])/3
                future_prior_data.append(mr_threeyravg)
                
                mr_price = mr_stock_price(ticker)
                future_prior_data.append(mr_price)
                print future_prior_data
                future_prior_data = np.array(future_prior_data, dtype=np.float32)
                print len(future_prior_data), '********'

            
        #############################################prior
            temp.append(float(cogs_prior[count-1]))
            feature_labels.append('cogs_prior')
            
            temp.append(float(float(sc_prior[count-1])))
            feature_labels.append('sc_prior')
            
            temp.append(float(fgs_prior[count-1]))
            feature_labels.append('fg_prior')
            
            temp.append(float(pred_prior[count-1]))
            feature_labels.append('pred_prior')
    
            temp.append(float(content['Return on Equity %'][str(years[count-1])+'-'+fye]))
            feature_labels.append('roe_prior')
    
            rev_prior = float(content['rev-Year over Year'][str(years[count-1])+'-'+fye])
            temp.append(rev_prior)
            feature_labels.append('revyoy_prior')
                  
            netmarg_prior = float(content['Net Margin %'][str(years[count-1])+'-'+fye])
            temp.append(netmarg_prior)
            feature_labels.append('netmarg_prior')
    
            temp.append(float(content['Earnings Per Share USD'][str(years[count-1])+'-'+fye]))
            feature_labels.append('eps_prior')

            temp.append(float(content['Debt/Equity'][str(years[count-1])+'-'+str(fye)])) #d-to-e prior year
            feature_labels.append('dtoe_prior')
            
            try:
                temp.append(float(content['Payout Ratio %'][str(years[count-1])+'-'+fye]))
                feature_labels.append('payout_prior')
            except:
                try:
                    payoutr = float(content['Dividends USD'][str(years[count-1])+'-'+str(fye)]) / float(content['Earnings Per Share USD'][str(years[count-1])+'-'+fye])
                    temp.append(payoutr)
                    feature_labels.append('payout_prior')
                except:
                    raise TypeError
                
            temp.append(float(threeavg[ticker][str(i)]))
            feature_labels.append('thryravgdgr')  
    
            temp.append(float(content['shareprices'][str(years[count-1])+'-'+str(fye)]))
            feature_labels.append('sp_prior')
            
            print len(temp), 'before first!'
        ############################################# combine:
            nd, glabels = gendata(temp, feature_labels)
            
            for q in glabels:
                feature_labels.append(q)
            
            for q in nd:
                temp.append(float(q))    
            print len(temp), 'before fred'
            for fo in fredobjs:
        #                print fo.metric
                start = str(years[count-1])+'-'+divmonth+'-01'
                end = str(years[count])+'-'+divmonth+'-01'
        #                print start, end
                mean, slope = calc_vals(start, end, fo.dates, fo.vals)
                temp.append(float(mean))
                temp.append(float(slope))   
        #                print mean, slope
        #                print
            
            for label in fred_labels:
                feature_labels.append(label)
                   
            nd, glabels = gendata(temp, feature_labels)
            
            for q in glabels:
                feature_labels.append(q)
            
            for q in nd:
                temp.append(float(q))    
            
            if labelsSaved == False:
                    
                joblib.dump(feature_labels, '/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_featlabels')
                labelsSaved = True
        
            temp = np.array(temp, np.float32)
            x.append(temp)
            y.append(float(content['divyoy'][str(years[count])+'-'+fye]))
            count += 1
    
    
        x = np.array(x, dtype = np.float32)
        y = np.array(y, dtype = np.float32)
        print years[-1]
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_mr_year', np.array([years[-1]]), delimiter = ',')
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_x', x, delimiter = ',')
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_y', y, delimiter = ',')
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_mr_price', np.array([mr_price], dtype= np.float32), delimiter=',')
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_future_prior', future_prior_data, delimiter=',')
        np.savetxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_mr_div', np.array([divs[-1]], dtype=np.float32), delimiter = ',')
    except:
        shutil.rmtree('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker)
        pass
