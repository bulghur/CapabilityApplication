import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools
import json

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config
from model import sql
from model import operateandmanage
template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))



def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')

class OperateProcess(webapp.RequestHandler):
    '''
    Initially displays the O&M page for Process Step Selection
    Uses: operateprocess
    '''
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
   
class CreateCase(webapp.RequestHandler): 
    '''Purpose: This object supports selection of PROCESS STEP, creation of the process case grouping
    and display of the resulting data set. 
    Display: operateprocess.html      
    '''
    
    def post(self): # post to DB
        
        idGenerator = config.IDGenerator()
        authenticateUser = str(users.get_current_user())
        case_key = str(idGenerator) + authenticateUser + self.request.get('proc_step_id')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO proc_case (case_nm, proc_step_id, emp_id, case_key) '
                       'VALUES (%s, %s, %s, %s)',
                       (
                       self.request.get('case_nm'),
                       self.request.get('proc_step_id'),
                       (authenticateUser),
                       (case_key),            
                       ))
        conn.commit()
        conn.close()
            
        authenticateUser = users.get_current_user()
        proc_step_id = self.request.get("proc_step_id")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        processAll = cursor.fetchall()
        
        cursor.execute("SELECT * FROM proc_req WHERE proc_step_id=%s", (proc_step_id))
        ddb_requirement = cursor.fetchall()

        '''        
        sqlscript = ("SELECT * FROM process_step WHERE proc_step_id=%s", (proc_step_id))
        c = sql.DoCustomQueries()
        c.query(sqlscript)
        ddb_proc_step = c.results
        '''
        
        cursor.execute("SELECT proc_case.case_id, proc_case.emp_id, proc_case.case_key, proc_req.proc_req_id, proc_req.proc_step_id, process.proc_id "
                            "FROM proc_case "
                            "INNER JOIN proc_req on (proc_case.proc_step_id = proc_req.proc_step_id) "
                            "INNER JOIN process_step on (proc_case.proc_step_id = process_step.proc_step_id) "
                            "INNER JOIN process on (process_step.proc_id = process.proc_id) "
                            " WHERE case_key = %s", (case_key))
        caseMake = cursor.fetchall()
   
        for row in caseMake:
            t = (row)
            cursor.execute("INSERT INTO proc_run (case_id, emp_id, case_key, proc_req_id, proc_step_id, proc_id) VALUES (%s, %s, %s, %s, %s, %s) ", t)  
        conn.commit()
        
    
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_case.case_nm, proc_run.emp_id, proc_run.case_key, " 
               "proc_run.proc_req_id, proc_req.proc_req_nm, proc_req.proc_req_seq, proc_req.proc_req_desc, proc_run.proc_step_id, "
               "process_step.proc_step_nm, process_step.proc_step_sop, process.proc_nm, proc_run.proc_output_conf "
               "FROM proc_run "
               "INNER JOIN proc_case on (proc_run.case_key = proc_case.case_key) "
               "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "  
               "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
               "INNER JOIN process on (proc_run.proc_id = process.proc_id) " 
               "WHERE proc_run.case_key = %s", (case_key))  
        case = cursor.fetchall()
        '''

        cursor.execute("SELECT proc_case.case_id, proc_case.case_nm, proc_case.emp_id, proc_case.case_key, proc_req.proc_req_id, proc_req.proc_req_nm, proc_req.proc_req_seq, "
                       "proc_req.proc_req_desc, proc_req.proc_step_id, process_step.proc_step_nm, process_step.proc_step_sop, process.proc_nm "
                            "FROM proc_case "
                            "INNER JOIN proc_req on (proc_case.proc_step_id = proc_req.proc_step_id) "
                            "INNER JOIN process_step on (proc_case.proc_step_id = process_step.proc_step_id) "
                            "INNER JOIN process on (process_step.proc_id = process.proc_id) ")  #" WHERE case_key = %s AND proc_output_conf IS NULL", (case_key))
        case = cursor.fetchall()
        '''
        '''
        rowArray_list = []
        for row in case:
            t = (row)
            rowArray_list.append(t)

        JSONcase = rowArray_list   
        
        if self.request.get('fmt') == "json": 
            #data = {'name': 'bob', 'age': 55, 'name': 'sally', 'age': 45}
            self.response.out.headers['Content-Type'] = ('text/json')
            self.response.out.write(JSONcase)
            return
        '''
        conn.close()     
        template_values = {'processAll': processAll, 'authenticateUser': authenticateUser, 'case': case} 
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
    
class PostProcessRun(webapp.RequestHandler): 
    def post(self): 
        now = config.UTCTime()
        authenticateUser = str(users.get_current_user())
        case_key = self.request.get('case_key')
        proc_output_conf = self.request.get('proc_output_conf')
        proc_conseq = self.request.get('proc_conseq')
        proc_innovation = self.request.get('proc_innovation')
        proc_run_id = self.request.get('proc_run_id')
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE proc_run SET "
                       "proc_run_start_tm =%s, proc_output_conf = %s, proc_conseq = %s, proc_innovation = %s "
                       "WHERE proc_run_id = %s ",
                       (now, proc_output_conf, proc_conseq, proc_innovation, proc_run_id))

        conn.commit()
        
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_case.case_nm, proc_run.emp_id, proc_run.case_key, " 
               "proc_run.proc_req_id, proc_req.proc_req_nm, proc_req.proc_req_seq, proc_req.proc_req_desc, proc_run.proc_step_id, "
               "process_step.proc_step_nm, process_step.proc_step_sop, process.proc_nm, proc_run.proc_output_conf "
               "FROM proc_run "
               "INNER JOIN proc_case on (proc_run.case_key = proc_case.case_key) "
               "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "  
               "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
               "INNER JOIN process on (proc_run.proc_id = process.proc_id) " 
               "WHERE proc_run.case_key = %s AND proc_run.proc_output_conf IS NULL ", (case_key))   
        case = cursor.fetchall()  
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()

        conn.close()
        
        template_values = {'ddb_process': ddb_process, 'authenticateUser': authenticateUser, 'case': case}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
