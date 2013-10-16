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

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

def get_connection():
    return rdbms.connect(host=config.HOST, db=config.DATABASE_NAME, user=config.USER_NAME, passwd=config.PASSWORD, charset='utf8')

class OperateProcess(webapp.RequestHandler):
    def get(self):
        conn = get_connection()
        cursor = conn.cursor()
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()
        conn.close()
        
        template_values = {'ddb_process': ddb_process,}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))

class SelectProcessStep(webapp.RequestHandler): 

    def post(self):
        
        proc_id = self.request.get("proc_id")
        proc_step_id = self.request.get("proc_step_id")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()

        cursor.execute("SELECT * FROM process_step where process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()

        cursor.execute("SELECT * FROM proc_req where proc_step_id=%s", (proc_step_id))
        ddb_requirement = cursor.fetchall()
        
        conn.close()
        
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'ddb_requirement': ddb_requirement,}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
        
class PostProcessRun(webapp.RequestHandler): # process run page
    def post(self): # post to DB
        sqlScript = "INSERT INTO proc_run (proc_run_start_tm, proc_run_end_tm, proc_input_conf, proc_output_conf, proc_input_comment, proc_output_comment, proc_req_id, emp_id, proc_run_status)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sqlScript, (
                       self.request.get("proc_run_start_tm"),
                       self.request.get("proc_run_end_tm"),
                       self.request.get('proc_input_conf'),
                       self.request.get('proc_output_conf'),
                       self.request.get('proc_input_comment'),
                       self.request.get('proc_output_comment'),
                       self.request.get('proc_req_id'),
                       self.request.get('emp_id'),
                       self.request.get('proc_run_status'),
                       ))
        conn.commit()
        conn.close()
        
        self.response.out.write(jinja2_env.get_template('operateprocess.html').render({}))