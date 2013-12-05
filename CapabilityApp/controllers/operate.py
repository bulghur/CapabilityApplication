import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools
import json
from array import *
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from controllers import home, design, utilities
from config import config, app_control
template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE,
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', 
                         use_unicode = True,
                         )
      
class OperateProcess(webapp.RequestHandler):
    '''
    Initially displays the O&M page for Process Step Selection
    Uses: operateprocess.html and sub_selector
    '''
    def get(self):
        
        conn = get_connection()
        cursor = conn.cursor()    
        
        authenticateUser = str(users.get_current_user())  
        
        cursor.execute("SELECT case_id, case_nm FROM proc_case WHERE status = 1 AND emp_id =%s", (authenticateUser))
        ddb_active_case = cursor.fetchall()

        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()  
        
        cursor.execute('SELECT * FROM process_step')
        ddb_proc_step = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        conn.close()

        template_values = {'ddb_proc_step': ddb_proc_step, 'ddb_active_case': ddb_active_case, 'ddb_process': ddb_process, 
                           'authenticateUser': authenticateUser, 'openoperations': openoperations}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class SelectProcessStep(webapp.RequestHandler):
    '''
    This process selects the parent process so that the process substeps can be easily selected.  
    '''
    def get(self):
        
        authenticateUser = str(users.get_current_user())
        proc_id = self.request.get("proc_id")
              
        conn = get_connection()
        cursor = conn.cursor()      
        
        cursor.execute("SELECT case_id, case_nm FROM proc_case WHERE status = 1 AND emp_id =%s", (authenticateUser))
        ddb_active_case = cursor.fetchall()

        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()  
                
        cursor.execute("SELECT * FROM process_step WHERE proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        conn.close()

        template_values = {'ddb_proc_step': ddb_proc_step, 'ddb_active_case': ddb_active_case, 'ddb_process': ddb_process, 'authenticateUser': authenticateUser}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class CreateCase(webapp.RequestHandler):
    '''
    This object creates a user case against which process run can be associated.  Cases are associated with specific users. 
    Renders to operateprocess.html.  
    '''
    def post(self):

        authenticateUser = str(users.get_current_user())
              
        conn = get_connection()
        cursor = conn.cursor()  
        
        cursor.execute('INSERT INTO proc_case (case_nm, emp_id, status) ' # status = 1 = ACTIVE
                       'VALUES (%s, %s, 1)',
                       (
                       self.request.get('case_nm'),
                       (authenticateUser),
                       ))   
        
        conn.commit() 
        
        cursor.execute("SELECT case_id, case_nm FROM proc_case WHERE status = 1 AND emp_id =%s", (authenticateUser))
        ddb_active_case = cursor.fetchall()

        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()  
                
        cursor.execute("SELECT * FROM process_step")
        ddb_proc_step = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()        
        
        conn.close()

        template_values = {'ddb_proc_step': ddb_proc_step, 'ddb_active_case': ddb_active_case, 'ddb_process': ddb_process, 'authenticateUser': authenticateUser}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
   
class CreateInstance(webapp.RequestHandler): 
    '''
    This object supports selection of PROCESS STEP, creation of the process case grouping, loading it into 
    the proc_run table and then pulls those entries back out to the display.  
    Instances are built off the concatenation of timefunction (secs since 1/01/1970 and the username@ function in config to 
    Ensure uniqueness.  If a process fails, it should be marked as a non-conformance and attempted again. 
    Display: operateprocess.html      
    TODO: Instances should load with status value set to initialised, then it should move to submitted or pending. 
    '''
    
    def post(self): # post to DB        
        idGenerator = config.IDGenerator() # generates a unique key
        authenticateUser = str(users.get_current_user())
        case_key = str(idGenerator) + authenticateUser
        now = config.UTCTime()
        
        conn = get_connection()
        cursor = conn.cursor()

        #create an unique instance key
        cursor.execute('INSERT INTO instance (case_id, proc_step_id, instance_key) '
                       'VALUES (%s, %s, %s)',
                       (
                        self.request.get('case_id'), 
                        self.request.get('proc_step_id'),  
                        (case_key)        
                       ))
        
        conn.commit()
        
        cursor.execute("SELECT proc_case.case_id, proc_case.emp_id, instance.instance_key, proc_req.proc_req_id, process_step.proc_step_id, process.proc_id "
                       "FROM proc_case "
                       "INNER JOIN instance on (proc_case.case_id = instance.case_id) "
                       "INNER JOIN process_step on (instance.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (process_step.proc_step_id = proc_req.proc_step_id) "
                       "INNER JOIN process on (process_step.proc_id = process.proc_id)"
                       "WHERE instance.instance_key = %s", (case_key))
        caseMake = cursor.fetchall()


        for row in caseMake:
            t = (row)
            cursor.execute("INSERT INTO proc_run (case_id, emp_id, instance_key, proc_req_id, proc_step_id, proc_id) VALUES (%s, %s, %s, %s, %s, %s) ", t)  
        conn.commit()

        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_run.emp_id, proc_run.instance_key, proc_run.proc_req_id, proc_run.proc_step_id, "
                       "process.proc_id, proc_case.case_nm, process.proc_nm, process_step.proc_step_nm, process_step.proc_step_sop, proc_run.proc_output_conf, "
                       "proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc, process_step.proc_model_link "
                       "FROM proc_run "
                       "INNER JOIN proc_case on (proc_run.case_id = proc_case.case_id) "
                       "INNER JOIN process on (proc_run.proc_id = process.proc_id) "
                       "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "INNER JOIN instance on (proc_run.instance_key = instance.instance_key) "
                       "WHERE instance.instance_key = %s", (case_key))
                        
                        
        case = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        conn.close() 
        
        template_values = {'authenticateUser': authenticateUser, 'case': case, 'case_key': case_key} 
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        self.response.out.write(case_key)
    
class PostProcessRun(webapp.RequestHandler): 
    '''
    This process posts the submission of each conforming or non-conforming requirement in seqence to the database.  
    ToDo: Remove the proc_run.proc_run_output IS NULL statement and instead display all the entries until the entire requirement 
    has been submitted. When no requirements exist to be fulfilled, then ask if the operator wants to exit or run another process. 
    '''
    def post(self): 
        now = config.UTCTime()
        authenticateUser = str(users.get_current_user())
        case_key = self.request.get('case_key')
        proc_output_conf = self.request.get('proc_output_conf')
        proc_notes = self.request.get('proc_notes')
        proc_conseq = self.request.get('proc_conseq')
        proc_innovation = self.request.get('proc_innovation')
        proc_run_id = self.request.get('proc_run_id')
        proc_run_status = self.request.get('proc_run_status')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE proc_run SET "
                       "proc_run_start_tm =%s, proc_output_conf = %s, proc_notes = %s, proc_conseq = %s, proc_innovation = %s, proc_run_status = %s "
                       "WHERE proc_run_id = %s",
                       (now, proc_output_conf, proc_notes, proc_conseq, proc_innovation, proc_run_status, proc_run_id ))

        conn.commit()
        
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_run.emp_id, proc_run.instance_key, proc_run.proc_req_id, proc_run.proc_step_id, "
                       "process.proc_id, proc_case.case_nm, process.proc_nm, process_step.proc_step_nm, process_step.proc_step_sop, proc_run.proc_output_conf, "
                       "proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc "
                       "FROM proc_run "
                       "INNER JOIN proc_case on (proc_run.case_id = proc_case.case_id) "
                       "INNER JOIN process on (proc_run.proc_id = process.proc_id) "
                       "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id)"
                       "WHERE proc_run.proc_output_conf IS NULL AND proc_run.instance_key = %s", (case_key))
        case = cursor.fetchall()  
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()

        conn.close()
        
        template_values = {'ddb_process': ddb_process, 'authenticateUser': authenticateUser, 'case': case, 'case_key': case_key, 
                           'openoperations': openoperations}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))

