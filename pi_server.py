# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:32:59 2015

@author: rm
"""
from __future__ import division
import random
import string
import os
import fit_new_data
import cherrypy
import numpy as np
from sklearn.externals import joblib
import datetime
import operator 
import json
class fred_data():
    def __init__(self, metric, dates, vals):
        self.dates = dates
        self.vals = vals
        self.metric = metric

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        welcome = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <link href="//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css"
          rel="stylesheet">
<title>Predict Dividend Growth Rates</title>          
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}
</style>

<html> <body> 
<link rel="icon" type="image/png" href="/favicon.ico?v=2">
<table class="tg" align="center">
  <tr>
    <th class="tg-031e"><b>Ticker</b></th>
    <th class="tg-031e"><b>Comapny Name</b></th>

    <th class="tg-031e"><b>Est Decl Date (overest.)</b></th>
  </tr>
<head> 
<center> <h3 class="text-primary">Expected Upcoming Dividend Increase Announcements:</h3> <hr></head> </center>
<center> <h6 class="text-info"> For increase announcements longer into the future (30+ days), potentially relevant macroeconomic data is not available.  </h6> </center>
"""
        upcoming_incs = joblib.load( '/home/ubuntu/dgrpred/dump/temp_persistence/upcoming_one_month')
        upcoming_incs_tm = joblib.load( '/home/ubuntu/dgrpred/dump/temp_persistence/upcoming_two_month')
        
        upcoming_incs_tm = sorted(upcoming_incs_tm.items(), key=operator.itemgetter(1))
#        upcoming_incs = upcoming_incs + upcoming_incs_tm
        folders = os.listdir('/home/ubuntu/dgrpred/dump/temp_persistence')
	fn_dict = joblib.load('/home/ubuntu/dgrpred/dump/fn_dict')
        for i in upcoming_incs_tm:
#            print i
            if i[0] in folders:
		fn = fn_dict[i[0].upper()]
                q = datetime.datetime.strftime(i[1], "%b %d, %Y")
                addition = """<tr>
                <td class="tg-031e"><a href="/compages?name=%s"> %s </a></td>
      		 <td class="tg-031e">%s</td>
                <td class="tg-031e">%s</td>
                </tr>""" % (i[0], i[0].upper(),fn, q)
                welcome += addition
        welcome += "</table><br><br></body></html> "
        return welcome


    @cherrypy.expose
    def compages(self, name):
        
        mr_year = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+name+'/'+name+'_mr_year')
        features_to_keep = joblib.load('/home/ubuntu/dgrpred/dump/temp_persistence/'+name+'/'+name+'_features_kept')
        feature_labels = joblib.load('/home/ubuntu/dgrpred/dump/temp_persistence/'+name+'/'+name+'_featlabels')
        
        end_future_feats =[]
        
        for i in features_to_keep:
            if 'future' in feature_labels[i]:
                q = feature_labels[i].split('/')
                for feat in q:
                    if 'future' in feat:
                        end_future_feats.append(feat)
        end_future_feats = list(set(end_future_feats))

        input_vals = []
        if 'revyoy_future' in end_future_feats or 'cogs_future' in end_future_feats or 'pred_future' in end_future_feats or 'sc_future' in end_future_feats or 'fg_future' in end_future_feats:
            input_vals.append('')
        else:
            input_vals.append(0)
            
        if 'eps_future' in end_future_feats or 'cogs_future' in end_future_feats or 'pred_future' in end_future_feats or 'sc_future' in end_future_feats or 'fg_future' in end_future_feats:
            input_vals.append('')
        else:
            input_vals.append(0)
            
        if 'roe_future' in end_future_feats or 'cogs_future' in end_future_feats or 'pred_future' in end_future_feats or 'sc_future' in end_future_feats or 'fg_future' in end_future_feats:
            input_vals.append('')
        else:
            input_vals.append(0)
            
        if 'netmarg_future' in end_future_feats:
            input_vals.append('')
        else:
            input_vals.append(0)
        
        if 'dtoe_future' in end_future_feats:
            input_vals.append('')
        else:
            input_vals.append(0)
        
        
#        print end_future_feats
        
        mr_year = int(mr_year)
        mr_next_year = mr_year + 1

        test_perf = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+name+'/'+name+'_test_perf', delimiter=',')

        last_actual, last_pred = str(round(test_perf[0], 3))+'%', str(round(test_perf[1], 3))+'%'
	fn_dict =joblib.load('/home/ubuntu/dgrpred/dump/fn_dict')        
        text = """

<!DOCTYPE html>
<html lang="en">
<link rel="icon" type="image/png" href="/favicon.ico?v=2">
<title>Predict Dividend Growth Rates </title>
  <head>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <link href="//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css"
          rel="stylesheet">
          
  <script type=text/javascript>
    $(function() {
      $('#calculate').bind('click', function() {
	$("#result").text("Processing ... ");

        $.getJSON('/predict', {
          revyoy: $('input[name="revyoy"]').val(),
          eps: $('input[name="eps"]').val(),
          roe: $('input[name="roe"]').val(),
          netmarg: $('input[name="netmarg"]').val(),
          dtoe: $('input[name="dtoe"]').val(),
          name: $('input[name="name"]').val(),
        }, function(data) {
          $("#result").text(data.result);
        });
        return false;
      });
    });
  </script>
  </head>
  <body>
    <div class="container">
      <div class="header"> 
        <h3 class="text-primary">Enter %d data for %s (%s)</h3>
      </div>
      <hr/>
      <div>
      <p>
    YOY Revenue (%%):&nbsp;&nbsp;&nbsp;<input type="text" size="5" value="%s" name="revyoy"> (est change from %d to %d)
     <div><p>
    EPS ($):&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" size="5" value="%s" name="eps"> 
     <div><p>
    ROE (%%):&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" size="5" value="%s" name="roe"> 
     <div><p>
    Net Margin (%%):&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" size="5" value="%s" name="netmarg">
     <div><p>
    Debt/Equity:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" size="5" value="%s" name="dtoe"> 
    <br>

    <form action= "javascript:void();">
    <br>
    <button type="button"  id="calculate" class="btn btn-success">Predict!</button>
    </form>
    <input value= %s input type="hidden" name="name">
    <p>
    <br>
    <b><code> Prediction: </b><span id="result">--</span></code>
      </form>
      </div>
    </div>
<br> Test set performance (last year):
<br>Prediction: %s
<br>Actual: %s
<hr/>

<h6 class="text-info"> *Note: If a zero appears in any input boxes, the coefficient for that feature is zero, and no user input is required.</h6>
<br>

<p class="text-left"><a href="/"> Home </a></p>
  </body>
</html>


""" % ( mr_next_year, fn_dict[name.upper()], name.upper(),  input_vals[0], mr_year, mr_next_year, input_vals[1], input_vals[2], input_vals[3], input_vals[4], name, last_pred, last_actual)
        return text
      
    @cherrypy.expose
    def predict(self, name, revyoy, eps, roe, netmarg, dtoe):
   #    show coeficients a
        print name, revyoy, eps, roe, netmarg, dtoe
        ticker = name
        pred = fit_new_data.fit(ticker, float(revyoy), float(eps), float(roe), float(netmarg), float(dtoe))
        prediction = str(round(pred[0], 3))+'%'
#        test_perf = np.loadtxt('/home/ubuntu/dgrpred/dump/temp_persistence/'+ticker+'/'+ticker+'_test_perf', delimiter=',')
#
#        last_actual, last_pred = str(round(test_perf[0], 3)), str(round(test_perf[1], 3))
#        d = test_perf[1] - test_perf[0]
#        last_residual = str(round(d, 3))
#        text = '''<a href="/"> Home </a><br><br>Next DG %% change prediction: <b>%s%%</b> <hr><br> Last Year Prediction: %s <br> <br> Last Year Actual: %s <br><br> Residual: %s''' %(prediction, last_pred, last_actual, last_residual)
#        home_link = '''
#<br>
#<br>
#<a href="/compages?name=%s"> Back </a>''' % (name)
#
#        text += home_link
#        return text
        t = json.dumps({'result':prediction})
        return t
        

    @cherrypy.expose
    def display(self):
        return cherrypy.session['mystring']

def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"

# set the priority according to your needs if you are hooking something
# else on the 'before_finalize' hook point.
cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize', secureheaders, priority=60)

if __name__ == '__main__':
     cherrypy.config.update({'server.socket_port': 80})
     cherrypy.server.socket_host = '0.0.0.0'
     conf = {
         '/': {
             'tools.sessions.on': True,
                'tools.sessions.secure' : True,
                'tools.sessions.httponly' : True,  
                'tools.secureheaders.on' : True,
		'log.access_file':'/home/ubuntu/access.log'
         },
	 '/favicon.ico':
		{
                'tools.staticfile.on': True,
                'tools.staticfile.filename': '/home/ubuntu/dgrpred/favicon.ico'
		}
     }
     cherrypy.quickstart(StringGenerator(), '/', conf)
