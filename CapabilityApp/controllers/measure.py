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
from google.appengine.ext import db
from google.appengine.api import users
from controllers import operate, home, design, utilities
from config import *
from array import *

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    )

class MeasurePerformance(webapp.RequestHandler):
    '''
    Queries on measurment 
    '''
    def get(self):

        conn = config.get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        
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
                       "WHERE (proc_conseq != ' ' OR not null OR proc_innovation != ' ' OR not null) AND proc_run.emp_id = %s "
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
                       "WHERE proc_run.emp_id = %s AND (proc_notes != '' OR not null) "
                       "ORDER BY process.proc_id, process_step.proc_step_id", (authenticateUser))                     
        notes = cursor.fetchall()
             
        conn.close()
        #query = ("SELECT * from person WHERE google_user_id ='" + str(authenticateUser) + "'")
        query = "SELECT * from person WHERE google_user_id = "
        condition1 = authenticateUser
        summary8 = database.query(query, condition1)
               
        template_values = {'summary': summary, 'sqlMeasurebyPerson' : sqlMeasurebyPerson, 'summary1': summary1, 'innovations': innovations, 
                           'authenticateUser': authenticateUser, 'processSummary': processSummary, 'notes': notes, 
                           'summary8': summary8, 'featureList': featureList}
        template = jinja2_env.get_template('measureperformance.html')
        self.response.out.write(template.render(template_values))
        
class PoncCalulator(webapp.RequestHandler):    
    def get(self):
        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        
        cursor.execute("SELECT DISTINCT proc_nm, proc_step_seq, proc_step_nm, proc_step_desc, proc_step_owner, proc_step_status, proc_step_ponc, "
                       "proc_step_poc, proc_step_efc "
                       "FROM vw_processes "
                       "WHERE proc_step_status = 'active' OR (proc_step_status = 'local' AND proc_step_owner = %s) "
                       "ORDER BY proc_id, proc_step_seq", (authenticateUser))
        processcost = cursor.fetchall()
                
        cursor.execute("SELECT proc_run_start_tm, proc_nm, proc_seq, proc_step_nm, case_nm, instance_key, emp_id, "
               "COUNT(proc_step_conf) AS tot_ops, SUM(proc_step_conf) AS tot_success, " #7, #9
               "(COUNT(proc_step_conf) - SUM(proc_step_conf)) AS failure, " #10
               "SUM(proc_ponc) AS sum_ponc, " #11
               "SUM(proc_poc) AS sum_poc, " #12
               "SUM(proc_efc) AS sum_efc, "  #13
               "(SUM(proc_poc) + SUM(proc_ponc)) AS tot_cost " #14
               "FROM vw_proc_run_sum "
               "WHERE emp_id = %s "
               "GROUP BY proc_step_id "
               "ORDER BY proc_id", (authenticateUser))
        capability = cursor.fetchall()
        conn.close()
               
        template_values = {'capability': capability, 'authenticateUser': authenticateUser, 'processcost': processcost, 'featureList': featureList}
        template = jinja2_env.get_template('ponccalculator.html')
        self.response.out.write(template.render(template_values))
 
        
            