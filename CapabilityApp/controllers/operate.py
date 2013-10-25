import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config
from dataqueries import sql
template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')

class OperateProcess(webapp.RequestHandler):
    def get(self):
        
        authenticateUser = users.get_current_user()
        proc_id = self.request.get("proc_id")
        proc_step_id = self.request.get("proc_step_id")
              
        conn = get_connection()
        cursor = conn.cursor()      
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()

        cursor.execute("SELECT * FROM process_step WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()
        
        conn.close()

        template_values = {'ddb_proc_step': ddb_process, 'ddb_proc_step': ddb_proc_step, 'authenticateUser': authenticateUser}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class SelectProcessStep(webapp.RequestHandler): 
    def get(self):
        
        authenticateUser = users.get_current_user()
        proc_id = OperateProcess(["proc_id"])
        proc_step_id = self.request.get("proc_step_id")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        d = "2"
        sqlscript = "SELECT * FROM proc_req WHERE proc_step_id=" + d
        
        c = sql.DoCustomQueries()
        c.query(sqlscript)
        ddb_proc_step = c.results
        
        cursor.execute("SELECT * FROM proc_req WHERE proc_step_id=%s", (proc_step_id))
        ddb_requirement = cursor.fetchall()
        
        sqlProcssSummary = "SELECT proc_nm, proc_step_nm, proc_seq, proc_req_desc, person.first_nm, person.last_nm FROM process inner join process_step ON (process.proc_id = process_step.proc_id) inner join person ON (process.emp_id = person.emp_id) inner join proc_req ON (process_step.proc_step_id = proc_req.proc_step_id);"
        cursor.execute(sqlProcssSummary)
        processSummary = cursor.fetchall()  
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        processAll = cursor.fetchall()
        '''
        sqlGetAllProcesses = "SELECT * FROM process where emp_id = 1 ORDER by proc_nm"
        processAll = c.query(sqlGetAllProcesses)
        '''
        conn.close()
        
        template_values = {'processAll': processAll, 'ddb_proc_step': ddb_proc_step, 'processSummary': processSummary, 'ddb_requirement': ddb_requirement,'authenticateUser': authenticateUser, 'proc_id': proc_id}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class PostProcessRun(webapp.RequestHandler): 
    def post(self): 
        now = config.UTCTime()
        sqlScript = "INSERT INTO proc_run (proc_run_start_tm, proc_run_end_tm, proc_output_conf, proc_input_comment, proc_output_comment, proc_req_id, emp_id, proc_run_status, proc_event)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sqlScript, (
                       (now),
                       (now),
                       self.request.get('proc_output_conf'),
                       self.request.get('proc_input_comment'),
                       self.request.get('proc_output_comment'),
                       self.request.get('proc_req_id'),
                       self.request.get('emp_id'),
                       self.request.get('proc_run_status'),
                       self.request.get('proc_event'),
                       ))
        conn.commit()
        conn.close()
        
        self.response.out.write(jinja2_env.get_template('operateprocess.html').render({}))
