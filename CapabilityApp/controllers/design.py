# bulghur-capability-01
import os
import cgi
import logging
import time
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#from ProcessRun import *

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8', use_unicode = True)

class PostProcessStep(webapp.RequestHandler):
    def post(self): # post to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO process_step (proc_step_nm, proc_seq, proc_step_desc, proc_id, proc_step_sop)'
                       'VALUES (%s, %s, %s, %s, %s)',
                       (
                       self.request.get('proc_step_nm'),
                       self.request.get('proc_seq'),
                       self.request.get('proc_step_desc'),
                       self.request.get('proc_id'),
                       self.request.get('proc_step_sop'),
                                                                                            
                       ))
        conn.commit()
        conn.close()
        self.redirect("/")
        
class PostProcessRequirement(webapp.RequestHandler):
    def post(self): # post to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO proc_req (proc_req_nm, proc_req_desc, proc_step_id)'
                       'VALUES (%s, %s, %s)',
                       (
                       self.request.get('proc_req_nm'),
                       self.request.get('proc_req_desc'),
                       self.request.get('proc_step_id'),
                                                                                            
                       ))
        conn.commit()
        conn.close()
        self.redirect("/")
   
class DevelopCapability(webapp.RequestHandler):
    def get(self):
        sqlMeasureAll = "SELECT person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, SUM(proc_run.proc_output_conf)/COUNT(*) FROM proc_run inner join person ON (proc_run.emp_id = person.emp_id) inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) inner join process ON (process_step.proc_id = process.proc_id) WHERE proc_run.proc_run_status='C' AND person.emp_id = 1 GROUP BY proc_run.emp_id, proc_run.proc_req_id"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sqlMeasureAll)
        rows = cursor.fetchall()
        conn.close()
    
        
        template_values = {'rows': rows, }
        template = jinja2_env.get_template('developcapability.html')
        self.response.out.write(template.render(template_values))    
        
        