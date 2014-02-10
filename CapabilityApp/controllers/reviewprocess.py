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
        
        if case_id is 'Choose Case':
            case_id = '%'
        else:
            pass
        
        conn = config.get_connection()
        cursor = conn.cursor()    
        cursor.execute("SELECT proc_nm, proc_step_nm, proc_run_start_tm, case_nm, case_id, instance_key, "
                       "emp_id, proc_step_conf "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       "AND case_id = %s "
                       "OR (proc_run_start_tm BETWEEN %s AND %s)"
                       "ORDER BY case_nm, proc_run_start_tm", (authenticateUser, case_id, proc_start_dt, proc_end_dt))
        reviewOperations = cursor.fetchall()
        
        conn.close()
        tabindex = 0

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'authenticateUser': authenticateUser, 
                           'reviewOperations': reviewOperations, 'featureList': featureList, 'tabindex': tabindex, 'case_id': case_id}
        template = jinja2_env.get_template('reviewprocess.html')
        self.response.out.write(template.render(template_values))
        
class CaseReview(webapp.RequestHandler):
        
    def post(self): 

        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        ddb_active_case = database.gaeSessionActiveCase()

        case_id = self.request.get('case_id')
        instance_key = self.request.get('instance_key')

        

        tabindex = 1

        template_values = {'ddb_active_case': ddb_active_case, 'processmenu': processmenu, 'authenticateUser': authenticateUser, 
                           'instance_key': instance_key, 'featureList': featureList, 'tabindex': tabindex, 'case_id': case_id}
        template = jinja2_env.get_template('reviewprocess.html')
        self.response.out.write(template.render(template_values))