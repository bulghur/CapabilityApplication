# bulghur-capability-01: Controls Home Page
import os
import cgi
import logging
import webapp2
import time
import jinja2
import itertools
import _mysql

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

backhome = os.path.join(os.path.dirname(__file__), 'index2.html')

#from ProcessRun import *

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

def get_connection():
    return rdbms.connect(host=config.HOST, db=config.DATABASE_NAME, user=config.USER_NAME, passwd=config.PASSWORD, charset='utf8')


class MainHandler(webapp.RequestHandler): 
    def get(self): # get from DB
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlScript = "SELECT proc_run.proc_req_id, person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm,SUM(proc_run.proc_output_conf)/COUNT(*), COUNT(*) FROM proc_run inner join person ON (proc_run.emp_id = person.emp_id) inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) inner join process ON (process_step.proc_id = process.proc_id) WHERE proc_run.proc_run_status='C' GROUP BY proc_run.emp_id, proc_run.proc_req_id"
        cursor.execute(sqlScript)
        rows = cursor.fetchall()
    
        sqlScript1 = "SELECT proc_nm, proc_step_nm, proc_step_desc FROM process inner join process_step ON (process_step.proc_id = process.proc_id)"
        cursor.execute(sqlScript1)
        processes = cursor.fetchall()
        
        conn.close()
    
        template_values = {"rows": rows, "processes": processes,}
        template = jinja2_env.get_template('index.html')
        self.response.out.write(template.render(template_values))