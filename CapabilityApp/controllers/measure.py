import os
import cgi
import logging
import time
import jinja2
import itertools
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from controllers import operate, home, design, utilities
from config import config, app_control
from config import myhandler

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
)


def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE,
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', 
                         use_unicode = True,
                         )

class MeasurePerformance(webapp.RequestHandler):
    def get(self):
        authenticateUser = users.get_current_user()
        authenticateUser = str(authenticateUser)
        summary = [] # creates the array
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_case.case_nm, "
                       "SUM(proc_run.proc_output_conf), COUNT(proc_run.proc_step_id), "
                       "SUM(proc_run.proc_output_conf)/COUNT(proc_run.proc_step_id) "
                       "FROM proc_run  "
                       "INNER JOIN proc_case ON (proc_run.case_id = proc_case.case_id) "       
                       "INNER JOIN process_step ON (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (proc_run.proc_id = process.proc_id) "
                       "WHERE proc_run.emp_id = %s "
                       "GROUP BY proc_run.proc_step_id "
                       "ORDER BY process.proc_id, process_step.proc_step_id",  (authenticateUser))    
        

        summary = cursor.fetchall()     
        summary1 = summary[1:4]  #2:3 specifies the row, not the column
        summary1 = summary1[1:4]

        cursor.execute("SELECT person.last_nm, process.proc_nm, SUM(proc_run.proc_output_conf)/COUNT(*) "
                       "FROM proc_run "
                       "inner join person ON (proc_run.emp_id = person.emp_id) "
                       "inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                       "inner join process ON (process_step.proc_id = process.proc_id) "
                       "WHERE proc_run.proc_run_status='C' GROUP BY proc_run.emp_id, process.proc_nm")
                       
        sqlMeasurebyPerson = cursor.fetchall()
        innovations = []
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_case.case_nm, proc_run_start_tm, "
                       "proc_conseq, proc_innovation, proc_run.emp_id "
                       "FROM proc_run "
                       "INNER JOIN proc_case ON (proc_run.case_id = proc_case.case_id) "      
                       "INNER JOIN process_step ON (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (proc_run.proc_id = process.proc_id) "
                       "WHERE proc_conseq IS NOT NULL OR proc_innovation IS NOT NULL "
                       "OR proc_conseq NOT LIKE '% %' OR proc_innovation NOT LIKE '% %' "
                       "ORDER BY process.proc_id, process_step.proc_step_id ")
                       
        innovations = cursor.fetchall()
        
        conn.close()
        
        template_values = {'summary': summary, 'sqlMeasurebyPerson' : sqlMeasurebyPerson, 'summary1': summary1, 'authenticateUser': authenticateUser, 'innovations': innovations}
        template = jinja2_env.get_template('measureperformance.html')
        self.response.out.write(template.render(template_values))
            