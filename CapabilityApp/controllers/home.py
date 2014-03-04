# bulghur-capability-01: Controls Home Page
import os
import cgi
import logging
import time
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import database, config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

authenticateUser = users.get_current_user()

class MainPageHandler(webapp.RequestHandler): #This is messy coding -- clean it up
        def get(self):
            authenticateUser = str(users.get_current_user()) 
            featureList = database.gaeSessionNavBuilder()
            user = database.gaeSessionUser()
            emp_id = user[0][0]
                        
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT proc_id, proc_nm, SUM(proc_step_conf), COUNT(proc_id), SUM(proc_step_conf)/COUNT(proc_id) AS conformance_rate, "
                           "SUM(proc_ponc), SUM(proc_poc), SUM(proc_efc) "
                           "FROM `capability`.`vw_proc_run_sum` "
                           "WHERE proc_run_start_tm > (NOW() - INTERVAL 7 DAY)"
                           "GROUP BY proc_id") 
            activitySummary = cursor.fetchall()
            conn.close()
            
            template_values = {"authenticateUser": authenticateUser, 'user': user, 'emp_id': emp_id, 'activitySummary': activitySummary, 'featureList': featureList}
            template = jinja2_env.get_template('index.html')
            self.response.out.write(template.render(template_values))