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
from config import config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#from ProcessRun import *

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, 
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8')

authenticateUser = str(users.get_current_user())  

class UtilityHandler(webapp.RequestHandler):
    def get(self):
       
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlGetAllPersons = "SELECT * FROM person ORDER by first_nm"
        cursor.execute(sqlGetAllPersons)
        ddb_person = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        cursor.execute("SELECT * FROM process_step "
                       "WHERE owner = 'organisation' OR %s "
                       "ORDER by proc_id", (authenticateUser))
        ddb_processsteps = cursor.fetchall()

        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_seq, proc_req.proc_req_nm, proc_req.proc_req_desc, "
                       "process.proc_desc, process_step.owner, process_step.proc_seq "
                       "FROM process_step "
                       "INNER JOIN process ON (process_step.proc_id = process.proc_id) "
                       "INNER JOIN proc_req ON (process_step.proc_step_id = proc_req.proc_step_id) "
                       "ORDER BY process.proc_id, process_step.proc_seq, proc_req.proc_req_seq")
        processlist = cursor.fetchall()
                
        conn.close()
        
        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps, 'processlist': processlist, 'authenticateUser': authenticateUser }
        template = jinja2_env.get_template('utilities.html')
        self.response.out.write(template.render(template_values))
        
class PostProcess(webapp.RequestHandler):
    def post(self): # post to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO process (proc_nm, proc_desc, emp_id, proc_start_dt) '
                       'VALUES (%s, %s, %s, %s)',
                       (
                       self.request.get('proc_nm'),
                       self.request.get('proc_desc'),
                       self.request.get('emp_id'),
                       self.request.get('proc_start_dt'),
                       ))
        conn.commit()
        conn.close()

        self.response.out.write(jinja2_env.get_template('utilities.html').render({}))
        
class PostProcessStep(webapp.RequestHandler):
    def post(self): # post to DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO process_step (proc_step_nm, proc_seq, proc_step_desc, proc_id, proc_step_sop, proc_model_link, owner)'
                       'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (
                       self.request.get('proc_step_nm'),
                       self.request.get('proc_seq'),
                       self.request.get('proc_step_desc'),
                       self.request.get('proc_id'),
                       self.request.get('proc_step_sop'),
                       self.request.get('proc_model_link'),
                       self.request.get('owner')
                                                                                            
                       ))
        conn.commit()
        conn.close()
        self.response.out.write(jinja2_env.get_template('utilities.html').render({}))
        
class PostRequirement(webapp.RequestHandler):
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

        self.response.out.write(jinja2_env.get_template('utilities.html').render({}))
        
class PostPerson(webapp.RequestHandler):
    def post(self): # post to DB
        conn = get_connection()
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