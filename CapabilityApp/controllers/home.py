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
from config import config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8', use_unicode = True)

###################    COMMON    ##############################

authenticateUser = users.get_current_user()

class MainHandler(webapp.RequestHandler): 
        def get(self):
            authenticateUser = users.get_current_user()
            email = authenticateUser.email()
            

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, SUM(proc_run.proc_output_conf)/COUNT(*), COUNT(proc_run.proc_output_conf) "
                           "FROM proc_run "
                           "INNER JOIN proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                           "INNER JOIN process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                           "INNER JOIN process ON (process_step.proc_id = process.proc_id) "
                           "GROUP BY process_step.proc_step_id, proc_req.proc_req_nm "
                           "ORDER BY process.proc_id, process_step.proc_seq") 
            processSummary = cursor.fetchall()
            conn.close()
            
            template_values = {"authenticateUser": authenticateUser, 'processSummary': processSummary}
            template = jinja2_env.get_template('index.html')
            self.response.out.write(template.render(template_values))