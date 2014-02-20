import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools
from gaesessions import get_current_session
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import memcache
from controllers import home, design, utilities
from config import *
from array import *

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    )

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    )

class ReviewCase(webapp.RequestHandler):
    
    def get(self):
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        openoperations = database.gaeSessionOpenOperations()
        
        tabindex = 0

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'authenticateUser': authenticateUser, 
                           'featureList': featureList, 'tabindex': tabindex, 'openoperations': openoperations}
        template = jinja2_env.get_template('reviewprocess.html')
        self.response.out.write(template.render(template_values))

class SelectReviewCase(webapp.RequestHandler):
        
    def post(self): 

        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()

        case_id = self.request.get('case_id')
        proc_start_dt = self.request.get('proc_start_dt')
        proc_end_dt = self.request.get('proc_end_dt')
        openProcesses = self.request.get('openProcesses')
        caseQueryString = ""
        dateQueryString = ""
        openProcessesQueryString = ""
        
        
        
        if not "Any Case" in case_id:
            caseQueryString = "AND case_id = '" + case_id + "' "
        else:
            caseQueryString = ""
        
        if proc_start_dt is not '' and proc_end_dt is not '':
            dateQueryString = "AND (proc_run_start_tm BETWEEN '" + proc_start_dt + "' AND '" + proc_end_dt + "') "
        else:
            dateQueryString = ""
            
        if proc_start_dt is not '' and '' in proc_end_dt:
            dateQueryString = "AND (proc_run_start_tm > '" + proc_start_dt + "') "
        else:
            pass

        if openProcesses is '':
            pass
        else:
            openProcessesQueryString = "AND proc_run_start_tm is NULL "
            dateQueryString = ""
        
        conn = config.get_connection()
        cursor = conn.cursor()    
        cursor.execute("SELECT proc_nm, proc_step_nm, proc_run_start_tm, case_nm, case_id, instance_key, "
                       "emp_id, proc_step_conf "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       + caseQueryString + dateQueryString + openProcessesQueryString +
                       "ORDER BY case_nm, proc_run_start_tm", (authenticateUser))
        reviewOperations = cursor.fetchall()
        
        conn.close()
        tabindex = 0

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'authenticateUser': authenticateUser, 
                           'reviewOperations': reviewOperations, 'featureList': featureList, 'tabindex': tabindex, 'case_id': case_id}
        template = jinja2_env.get_template('reviewprocess.html')
        self.response.out.write(template.render(template_values))
        
      
class EditInstance(webapp.RequestHandler):
    '''
This object allows the user to edit the selected instance. This redirects the user back to the operate.py controller.  Perhaps this should be put there?
'''
    
    def get(self): # post to DB
        authenticateUser = str(users.get_current_user())
        idGenerator = config.IDGenerator() # generates a unique key
        instance_key = str(idGenerator) + authenticateUser
        now = config.UTCTime()
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        case_id = self.request.get('case_id')
        proc_step_id = self.request.get('proc_step_id')
        
        instance_key = self.request.get('instance_key') # ALL THESE INSTANCE idS NEED TO BE CHANGED TO key
        session = get_current_session()
        session.set_quick('instance_key', instance_key)
        session.set_quick('case_id', case_id)
        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE proc_run SET proc_run_status = 1 "
                       "WHERE instance_key = %s ", instance_key)
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
                       "WHERE instance.instance_key = %s", (instance_key))
                        
        tabindex = 2                
        instance = cursor.fetchall()
        
        conn.close()

        template_values = {'authenticateUser': authenticateUser, 'instance': instance, 'case_id': case_id, 'processmenu': processmenu, 'featureList': featureList,
                           'ddb_active_case': ddb_active_case, 'ddb_active_case': ddb_active_case, 'tabindex': tabindex }
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        self.response.out.write(case_id)