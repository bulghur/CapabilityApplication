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
from config import *
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

        summary = []
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       "GROUP BY proc_step_id, proc_id, case_id "
                       "ORDER BY proc_nm, case_nm, proc_seq", (authenticateUser))        

        summary = cursor.fetchall()     
        summary1 = summary[1:1]  #2:3 specifies the row, not the column
        summary1 = summary1[1:4]
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       "GROUP BY proc_step_id "
                       "ORDER BY proc_nm, proc_seq, case_nm", (authenticateUser))     
                      
        sqlMeasurebyPerson = cursor.fetchall()
        
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_case.case_nm, proc_run_start_tm, "
                       "proc_conseq, proc_innovation, proc_run.emp_id "
                       "FROM proc_run "
                       "INNER JOIN proc_case ON (proc_run.case_id = proc_case.case_id) "      
                       "INNER JOIN process_step ON (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (proc_run.proc_id = process.proc_id) "
                       "WHERE proc_run.emp_id = %s AND (proc_conseq != ' ' OR not null OR proc_innovation != ' ' OR not null) "
                       "ORDER BY process.proc_id, process_step.proc_step_id", (authenticateUser))                     
        innovations = cursor.fetchall()
        

        cursor = conn.cursor()
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, SUM(proc_run.proc_output_conf)/COUNT(*), COUNT(proc_run.proc_output_conf) "
                       "FROM proc_run "
                       "INNER JOIN proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "INNER JOIN process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (process_step.proc_id = process.proc_id) "
                       "GROUP BY process_step.proc_step_id, proc_req.proc_req_nm "
                       "ORDER BY process.proc_id, process_step.proc_seq") 
        processSummary = cursor.fetchall()
        
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_case.case_nm, proc_run_start_tm, "
                       "proc_notes, proc_conseq, proc_innovation, proc_run.emp_id "
                       "FROM proc_run "
                       "INNER JOIN proc_case ON (proc_run.case_id = proc_case.case_id) "      
                       "INNER JOIN process_step ON (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (proc_run.proc_id = process.proc_id) "
                       "WHERE proc_run.emp_id = %s AND (proc_notes != ' ' OR not null) "
                       "ORDER BY process.proc_id, process_step.proc_step_id", (authenticateUser))                     
        notes = cursor.fetchall()
    
        
        conn.close()
        #query = ("SELECT * from person WHERE google_user_id ='" + str(authenticateUser) + "'")
        query = "SELECT * from person WHERE google_user_id = "
        condition1 = authenticateUser
        summary8 = database.query(query, condition1)
        
        
        '''
        def main():
            print(sumProblemString(2, 3))
            print(sumProblemString(1234567890123, 535790269358))
            a = int(input("Enter an integer: "))
            b = int(input("Enter another integer: "))
            print(sumProblemString(a, b))
        
        main() 
        '''
        
        template_values = {'summary': summary, 'sqlMeasurebyPerson' : sqlMeasurebyPerson, 'summary1': summary1, 'authenticateUser': authenticateUser, 'innovations': innovations,
                           "authenticateUser": authenticateUser, 'processSummary': processSummary, 'notes': notes, 'summary8': summary8 }
        template = jinja2_env.get_template('measureperformance.html')
        self.response.out.write(template.render(template_values))
            