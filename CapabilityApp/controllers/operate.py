import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools
# import MySQLdb
from gaesessions import get_current_session
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from controllers import home, design, utilities
from config import *
from array import *

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    )
           
class OperateProcess(webapp.RequestHandler):
    '''
    Initially displays the O&M page for Process Step Selection
    Uses: operateprocess.html and sub_selector
    '''
    def get(self):
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        
        conn = config.get_connection()
        cursor = conn.cursor()    
        '''
        cursor.execute("SELECT case_id, case_nm FROM proc_case WHERE status = 1 AND emp_id =%s", (authenticateUser))
        ddb_active_case = cursor.fetchall()
        '''
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        conn.close()
        tabindex = 2

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'authenticateUser': authenticateUser, 
                           'openoperations': openoperations, 'featureList': featureList, 'tabindex': tabindex}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class CreateInstance(webapp.RequestHandler):
    '''
This object supports selection of PROCESS STEP, creation of the process case grouping, loading it into
the proc_run table and then pulls those entries back out to the display.
Instances are built off the concatenation of timefunction (secs since 1/01/1970 and the username@ function in config to
Ensure uniqueness. If a process fails, it should be marked as a non-conformance and attempted again.
Display: operateprocess.html
TODO: Instances should load with status value set to initialised, then it should move to submitted or pending.
'''
    
    def post(self): # post to DB
        authenticateUser = str(users.get_current_user())
        idGenerator = config.IDGenerator() # generates a unique key
        instance_id = str(idGenerator) + authenticateUser
        now = config.UTCTime()
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        case_id = self.request.get('case_id')
        proc_step_id = self.request.get('proc_step_id')
        
        session = get_current_session()
        session.set_quick('instance_id', instance_id)
        session.set_quick('case_id', case_id)
        
        conn = config.get_connection()
        cursor = conn.cursor()

        #create an unique instance key
        cursor.execute('INSERT INTO instance (case_id, proc_step_id, instance_key) '
                       'VALUES (%s, %s, %s)',
                       (
                        (case_id),
                        (proc_step_id),
                        (instance_id)
                       ))
        
        conn.commit()
        
        cursor.execute("SELECT proc_case.case_id, proc_case.emp_id, instance.instance_key, proc_req.proc_req_id, process_step.proc_step_id, process.proc_id "
                       "FROM proc_case "
                       "INNER JOIN instance on (proc_case.case_id = instance.case_id) "
                       "INNER JOIN process_step on (instance.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (process_step.proc_step_id = proc_req.proc_step_id) "
                       "INNER JOIN process on (process_step.proc_id = process.proc_id)"
                       "WHERE instance.instance_key = %s", (instance_id))
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
                       "WHERE instance.instance_key = %s", (instance_id))
                        
        tabindex = 3                
        instance = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()
        
        conn.close()

        template_values = {'authenticateUser': authenticateUser, 'instance': instance, 'case_id': case_id, 'processmenu': processmenu, 'featureList': featureList,
                           'ddb_active_case': ddb_active_case, 'ddb_active_case': ddb_active_case, 'tabindex': tabindex, 'openoperations': openoperations }
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        self.response.out.write(case_id)
    
class PostInstance(webapp.RequestHandler): 
    '''
    This process posts the submission of each conforming or non-conforming requirement in sequence to the database.  
    ToDo: Remove the proc_run.proc_run_output IS NULL statement and instead display all the entries until the entire requirement 
    has been submitted. When no requirements exist to be fulfilled, then ask if the operator wants to exit or run another process. 
    '''
    def post(self): 
        now = config.UTCTime()
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        proc_output_conf = self.request.get('proc_output_conf')
        proc_notes = self.request.get('proc_notes')
        proc_conseq = self.request.get('proc_conseq')
        proc_innovation = self.request.get('proc_innovation')
        proc_run_id = self.request.get('proc_run_id')
        proc_run_status = "pending"
        
        session = get_current_session()
        instance_id = session.get('instance_id')
        case_id = session.get('case_id')
        
        conn = config.get_connection()
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
                       "WHERE proc_run.proc_output_conf IS NULL AND proc_run.instance_key = %s", (instance_id))
        
        instanceCount = cursor.rowcount
        instance = cursor.fetchall()  
        
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()

        conn.close()
        
        if instanceCount > 0:
            tabindex = 3
            template_values = {'processmenu': processmenu, 'authenticateUser': authenticateUser, 'instance': instance, 'case_id': case_id, 
                           'openoperations': openoperations, 'ddb_active_case': ddb_active_case, 'featureList': featureList,
                           'tabindex': tabindex}
            template = jinja2_env.get_template('operateprocess.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/AssessPerformance")
            

class AssessPerformance(webapp.RequestHandler):
    '''
    This displays the completed process step so that the process operator can assess their behaviour against the 
    performance standard.
    '''
    def get(self):
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        session = get_current_session()
        instance_id = session.get('instance_id')
        
        tabindex = 4
        conn = config.get_connection()
        cursor = conn.cursor()    
        
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.emp_id, proc_run.instance_key, proc_case.case_nm, process.proc_nm, process_step.proc_step_nm, "
                       "proc_run.proc_output_conf, proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc, proc_run.proc_notes, "
                       "proc_run.proc_conseq, proc_run.proc_innovation "
                       "FROM proc_run "
                       "INNER JOIN proc_case on (proc_run.case_id = proc_case.case_id) "
                       "INNER JOIN process on (proc_run.proc_id = process.proc_id) "
                       "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "WHERE proc_run.instance_key = %s", (instance_id)) 
        
        instance = cursor.fetchall()  
        
        conn.close()

        template_values = {'authenticateUser': authenticateUser, 'featureList': featureList, 'tabindex': tabindex,
                           'instance': instance, 'instance_id': instance_id }
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class PostProcessAssessment(webapp.RequestHandler): 
    '''
    This handler loads the completed process step on to the Assessment page and then sets it up so that the user can assess
    their behaviour and submit it.  The key is case_id (name should be changed) as stored in memcache.  Plan to use JS to load the 
    tickboxes    
    '''
    def post(self): 
        now = config.UTCTime()
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        
        perf_stnd_1 = self.request.get('perf_stnd_1')
        perf_stnd_2 = self.request.get('perf_stnd_2')
        perf_stnd_3 = self.request.get('perf_stnd_3')
        perf_stnd_notes_1 = self.request.get('perf_stnd_notes_1')
        perf_stnd_notes_2 = self.request.get('perf_stnd_notes_2')
        perf_stnd_notes_3 = self.request.get('perf_stnd_notes_3')
        session = get_current_session()
        instance_id = session.get('instance_id')
        
        if perf_stnd_1 is '':
            perf_stnd_1 = 0
        else:
            perf_stnd_1 = 1
        if perf_stnd_2 is '':
            perf_stnd_2 = 0
        else:
            perf_stnd_2 = 1
        if perf_stnd_3 is '':
            perf_stnd_3 = 0
        else:
            perf_stnd_3 = 1
            
        if instance_id is None:
            pass # query for last entry for expired GAE Sessions
        else:
            pass 
        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        #perf_stnd_1 =%s, perf_stnd_2 = %s, perf_stnd_3 = %s, // perf_stnd_1, perf_stnd_2, perf_stnd_3, //perf_stnd_notes_ts
        cursor.execute("UPDATE instance SET "
                       "perf_stnd_1 = %s, perf_stnd_2 = %s,perf_stnd_3 = %s, perf_stnd_notes_1 = %s, perf_stnd_notes_2 = %s, perf_stnd_notes_3 = %s, perf_stnd_notes_ts = %s "
                       "WHERE instance_key = %s ",
                       (perf_stnd_1, perf_stnd_2, perf_stnd_3, perf_stnd_notes_1, perf_stnd_notes_2, perf_stnd_notes_3, now, instance_id ))
        conn.commit()
        
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_run.emp_id, proc_run.instance_key, proc_run.proc_req_id, proc_run.proc_step_id, "
                       "process.proc_id, proc_case.case_nm, process.proc_nm, process_step.proc_step_nm, process_step.proc_step_sop, proc_run.proc_output_conf, "
                       "proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc, process_step.proc_model_link, proc_run.proc_notes "
                       "FROM proc_run "
                       "INNER JOIN proc_case on (proc_run.case_id = proc_case.case_id) "
                       "INNER JOIN process on (proc_run.proc_id = process.proc_id) "
                       "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "INNER JOIN instance on (proc_run.instance_key = instance.instance_key) "
                       "WHERE instance.instance_key = %s ", (instance_id))
        instance = cursor.fetchall()
        
        cursor.execute("SELECT perf_stnd_1, perf_stnd_2, perf_stnd_3, perf_stnd_notes_1, perf_stnd_notes_2, perf_stnd_notes_3 "
                       "FROM instance "
                       "WHERE instance_key = %s", (instance_id))
        instanceperformance = cursor.fetchall()

        conn.close()       

        tabindex = 5
        
        template_values = {'processmenu': processmenu, 'authenticateUser': authenticateUser, 'ddb_active_case': ddb_active_case, 'featureList': featureList,
                           'tabindex': tabindex, 'instance': instance, 'instance_id': instance_id, 'instanceperformance': instanceperformance}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class PostConsequences(webapp.RequestHandler): #rename
    '''
    This handler loads the completed process step on to the Assessment page and then sets it up so that the user can assess
    their behaviour and submit it.  The key is case_id (name should be changed) as stored in memcache.  Plan to use JS to load the 
    tickboxes    
    '''
    def post(self): 
        now = config.UTCTime()
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()
        proc_conseq = self.request.get('proc_conseq')
        proc_innovation = self.request.get('proc_innovation')
        proc_run_id = self.request.get('proc_run_id')
        proc_run_status = 'complete'
        session = get_current_session()
        instance_id = session.get('instance_id')
                
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE proc_run SET "
                       "proc_conseq = %s, proc_innovation = %s, proc_run_status = %s "
                       "WHERE proc_run_id = %s",
                       (proc_conseq, proc_innovation, proc_run_status, proc_run_id ))
        instance = cursor.fetchall()
        
        cursor.execute("SELECT proc_run.proc_run_id, proc_run.case_id, proc_run.emp_id, proc_run.instance_key, proc_run.proc_req_id, proc_run.proc_step_id, "
               "process.proc_id, proc_case.case_nm, process.proc_nm, process_step.proc_step_nm, process_step.proc_step_sop, proc_run.proc_output_conf, "
               "proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc, process_step.proc_model_link, proc_run.proc_notes "
               "FROM proc_run "
               "INNER JOIN proc_case on (proc_run.case_id = proc_case.case_id) "
               "INNER JOIN process on (proc_run.proc_id = process.proc_id) "
               "INNER JOIN process_step on (proc_run.proc_step_id = process_step.proc_step_id) "
               "INNER JOIN proc_req on (proc_run.proc_req_id = proc_req.proc_req_id) "
               "INNER JOIN instance on (proc_run.instance_key = instance.instance_key) "
               "WHERE proc_run.proc_run_status = 'pending' AND proc_run.instance_key = %s", (instance_id))
        instance = cursor.fetchall()
        instanceCount = cursor.rowcount
        
        cursor.execute("SELECT perf_stnd_1, perf_stnd_2, perf_stnd_3, perf_stnd_notes_1, perf_stnd_notes_2, perf_stnd_notes_3 "
                       "FROM instance "
                       "WHERE instance_key = %s", (instance_id))
        instanceperformance = cursor.fetchall()
        
        conn.commit()
        conn.close()      
        
        if instanceCount > 0:
            tabindex = 5
        else:
            tabindex = 2 

        
        template_values = {'processmenu': processmenu, 'authenticateUser': authenticateUser, 'ddb_active_case': ddb_active_case, 'featureList': featureList,
                           'tabindex': tabindex, 'instance': instance, 'instanceperformance': instanceperformance}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
        
class CreateCase(webapp.RequestHandler):
    '''
    This object creates a user case against which process run can be associated.  Cases are associated with specific users. 
    Renders to operateprocess.html.  
    '''
    def post(self):
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        openoperations = database.gaeSessionOpenOperations()

        conn = config.get_connection()
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
        
        session = get_current_session()
        session.set_quick('ddb_active_case', ddb_active_case)
      
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null AND emp_id = %s", (authenticateUser))
        openoperations = cursor.fetchall()  
        
        conn.close()
        
        tabindex = 2

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'openoperations': openoperations, 
                           'authenticateUser': authenticateUser, 'tabindex': tabindex, 'featureList': featureList }
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(template_values))
    
