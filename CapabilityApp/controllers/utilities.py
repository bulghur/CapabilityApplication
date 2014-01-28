# bulghur-capability- This module manages back end support.  Some of these functions will migrate to the 
# Design Module
import os
import cgi
import logging
import time
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from config import *
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#from ProcessRun import *

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

class DevelopCapability(webapp.RequestHandler):
    def get(self): 
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, "
                       "SUM(proc_run.proc_output_conf)/COUNT(*) "
                       "FROM proc_run "
                       "inner join person ON (proc_run.emp_id = person.emp_id) "
                       "inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                       "inner join process ON (process_step.proc_id = process.proc_id) "
                       "WHERE proc_run.proc_run_status='C' AND person.emp_id = 1 "
                       "GROUP BY proc_run.emp_id, proc_run.proc_req_id")
        rows = cursor.fetchall()
        conn.close()
    
        
        template_values = {'rows': rows, }
        template = jinja2_env.get_template('developcapability.html')
        self.response.out.write(template.render(template_values)) 

class UtilityHandler(webapp.RequestHandler):
    def get(self):
        
        authenticateUser = str(users.get_current_user())
        featureList = database.memcacheNavBuilder()  
       
        conn = config.get_connection()
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT * FROM person ORDER by first_nm")
        ddb_person = cursor.fetchall()
        

        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()


        cursor.execute("SELECT * FROM process_step ORDER by proc_step_nm")
        ddb_processsteps = cursor.fetchall()

        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'active'")
        processlist = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'local' AND proc_step_owner = %s", (authenticateUser))
        localprocesslist = cursor.fetchall()
                
        conn.close()
        
        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps, 
                           'processlist': processlist, 'localprocesslist': localprocesslist, 'authenticateUser': authenticateUser, 'featureList': featureList }
        template = jinja2_env.get_template('utilities.html')
        self.response.out.write(template.render(template_values))
        
        
        
class PostProcess(webapp.RequestHandler):
    def post(self): # post to DB
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.memcacheNavBuilder() 
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO process (proc_nm, proc_desc, proc_owner, proc_start_dt) '
                       'VALUES (%s, %s, %s, %s)',
                       (
                       self.request.get('proc_nm'),
                       self.request.get('proc_desc'),
                       self.request.get('emp_id'),
                       self.request.get('proc_start_dt')
                       ))
        conn.commit()
        
        cursor.execute("SELECT * FROM person ORDER by first_nm")
        ddb_person = cursor.fetchall()
        
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process_step ORDER by proc_step_nm")
        ddb_processsteps = cursor.fetchall()

        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'active'")
        processlist = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'local' AND proc_step_owner = %s", (authenticateUser))
        localprocesslist = cursor.fetchall()
                
        conn.close()
        
        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps, 
                           'processlist': processlist, 'localprocesslist': localprocesslist, 'authenticateUser': authenticateUser,
                           'featureList': featureList }
        template = jinja2_env.get_template('utilities.html')
        self.response.out.write(template.render(template_values))
     
        dialoguemessage  = '<b>' + self.request.get('proc_nm') + '</b>' + ' successfully created.'
        dialoguetitle = "Create Process"
        
        dialoguebox = {'dialoguemessage': dialoguemessage, 'dialoguetitle': dialoguetitle}
        template = jinja2_env.get_template('dialoguebox.html')
        self.response.out.write(template.render(dialoguebox))
     
class PostProcessStep(webapp.RequestHandler):
    def post(self): # post to DB
        
        authenticateUser = str(users.get_current_user())  
        featureList = database.memcacheNavBuilder() 
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO process_step (proc_step_nm, proc_seq, proc_step_desc, proc_id, proc_step_sop, proc_model_link, process_step.proc_step_owner, "
                       "proc_poc, proc_ponc, proc_efc ) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (
                       self.request.get('proc_step_nm'),
                       self.request.get('proc_seq'),
                       self.request.get('proc_step_desc'),
                       self.request.get('proc_id'),
                       self.request.get('proc_step_sop'),
                       self.request.get('proc_model_link'),
                       self.request.get('owner'),
                       self.request.get('proc_poc'),
                       self.request.get('proc_ponc'),
                       self.request.get('proc_efc')                                                                                
                       ))
        conn.commit()
        
        cursor.execute("SELECT * FROM person ORDER by first_nm")
        ddb_person = cursor.fetchall()
        

        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process_step ORDER by proc_step_nm")
        ddb_processsteps = cursor.fetchall()

        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'active'")
        processlist = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'local' AND proc_step_owner = %s", (authenticateUser))
        localprocesslist = cursor.fetchall()
                
        conn.close()
        
        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps, 
                          'processlist': processlist, 'localprocesslist': localprocesslist, 'authenticateUser': authenticateUser,
                          'featureList': featureList }
        template = jinja2_env.get_template('utilities.html')
        self.response.out.write(template.render(template_values))
     
        dialoguemessage  = self.request.get('<b>proc_step_nm</b>') + " successfully created."
        
        template_values1 = {'dialoguemessage': dialoguemessage}
        template = jinja2_env.get_template('dialoguebox.html')
        self.response.out.write(template.render(template_values1))
        
class PostRequirement(webapp.RequestHandler):
    def post(self): 
        
        authenticateUser = str(users.get_current_user())
        featureList = database.memcacheNavBuilder()  
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO proc_req (proc_req_nm, proc_req_desc, proc_req_seq, proc_step_id)'
                       'VALUES (%s, %s, %s, %s)',
                       (
                       self.request.get('proc_req_nm'),
                       self.request.get('proc_req_desc'),
                       self.request.get('proc_req_seq'), 
                       self.request.get('proc_step_id'),                                  
                       ))
        conn.commit()

        cursor.execute("SELECT * FROM person")
        ddb_person = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process_step ORDER by proc_step_nm")
        ddb_processsteps = cursor.fetchall()

        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'active'")
        processlist = cursor.fetchall()
        
        cursor.execute("SELECT * FROM capability.vw_processes WHERE proc_step_status = 'local' AND proc_step_owner = %s", (authenticateUser))
        localprocesslist = cursor.fetchall()
                
        conn.close()
        
        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps, 
                           'processlist': processlist, 'localprocesslist': localprocesslist, 'authenticateUser': authenticateUser,
                           'featureList': featureList }
        template = jinja2_env.get_template('utilities.html')
        self.response.out.write(template.render(template_values))
     
        dialoguemessage  = self.request.get('proc_req_nm') + " successfully created."
        
        template_values1 = {'dialoguemessage': dialoguemessage}
        template = jinja2_env.get_template('dialoguebox.html')
        self.response.out.write(template.render(template_values1))
        
class PostPerson(webapp.RequestHandler):
    def post(self): # post to DB
        
        authenticateUser = str(users.get_current_user())  
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO person (first_nm, last_nm, email)'
                       'VALUES (%s, %s, %s)',
                       (
                       self.request.get('first_nm'),
                       self.request.get('last_nm'),
                       self.request.get('email'),
                                                                                            
                       ))
        conn.commit()
        conn.close()

        self.response.out.write(jinja2_env.get_template('utilities.html').render({}))