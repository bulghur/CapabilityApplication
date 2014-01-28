# bulghur-capability-01
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

class PostProcessStep(webapp.RequestHandler):
    def post(self): # post to DB
        conn = config.get_connection()
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
        self.redirect("/")
        
class PostProcessRequirement(webapp.RequestHandler):
    def post(self): # post to DB
        conn = config.get_connection()
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
        self.redirect("/")
   
   
        
        