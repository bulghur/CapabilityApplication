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
from config import config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#from ProcessRun import *

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')



class UtilityHandler(webapp.RequestHandler):
    def get(self):
        #self.response.out.write(jinja2_env.get_template('utilities.html').render({}))
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlGetAllPersons = "SELECT * FROM person ORDER by first_nm"
        cursor.execute(sqlGetAllPersons)
        ddb_person = cursor.fetchall()
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()
        
        sqlGetAllProcessSteps = "SELECT * FROM process_step ORDER by proc_id"
        cursor.execute(sqlGetAllProcessSteps)
        ddb_processsteps = cursor.fetchall()
        
        conn.close()

        template_values = {'ddb_person': ddb_person, 'ddb_process': ddb_process, 'ddb_processsteps': ddb_processsteps }
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