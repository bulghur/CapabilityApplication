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

class MeasureOperatorPerformance(webapp2.RequestHandler):
    '''
    Queries on measurement 
    '''
    def get(self):

        conn = config.get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       "GROUP BY proc_step_id, proc_id "
                       "ORDER BY proc_nm, proc_seq", (authenticateUser))        
        summaryByProcess = cursor.fetchall() #This table displays your personal performance as an Operator.    
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s "
                       "GROUP BY case_id, proc_id, proc_step_id "
                       "ORDER BY proc_nm, proc_seq, case_nm ", (authenticateUser))        

        summaryByCase = cursor.fetchall()           
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE proc_id = 14 OR proc_id = 15 "
                       "GROUP BY proc_step_id "
                       "ORDER BY proc_nm, proc_seq, case_nm")    
        orgProcesses = cursor.fetchall() #Individual "local" processes are not included in this summary.
        
        cursor.execute("SELECT proc_nm, proc_step_nm, case_nm, instance_key, proc_run_start_tm, "
                       "proc_conseq, proc_innovation, emp_id, perf_stnd_notes_1, perf_stnd_notes_2, perf_stnd_notes_3 "
                       "FROM vw_proc_run_sum "
                       "WHERE emp_id = %s AND "
                       "(proc_conseq != ' ' OR not null "
                       "OR proc_innovation != ' '  OR not null "
                       "OR perf_stnd_notes_1 != ' '  OR not null "
                       "OR perf_stnd_notes_2 != ' '  OR not null "
                       "OR perf_stnd_notes_3 != ' '  OR not null) "
                       "ORDER BY proc_nm, proc_step_nm, instance_key ", (authenticateUser))               
        consequencesAndAdjustments = list(cursor.fetchall())

        
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_case.case_nm, proc_run_start_tm, "
                       "proc_notes, proc_conseq, proc_innovation, proc_run.emp_id, proc_run.instance_key "
                       "FROM proc_run "
                       "INNER JOIN proc_case ON (proc_run.case_id = proc_case.case_id) "      
                       "INNER JOIN process_step ON (proc_run.proc_step_id = process_step.proc_step_id) "
                       "INNER JOIN process ON (proc_run.proc_id = process.proc_id) "
                       "WHERE proc_run.emp_id = %s AND (proc_notes != '' OR not null) "
                       "ORDER BY process.proc_id, process_step.proc_step_id", (authenticateUser))                     
        notes = cursor.fetchall()
        
        cursor.execute("SELECT proc_run_start_tm, proc_nm, proc_seq, proc_step_nm, case_nm, instance_key, emp_id, "
               "COUNT(proc_step_conf) AS tot_ops, SUM(proc_step_conf) AS tot_success, " 
               "(COUNT(proc_step_conf) - SUM(proc_step_conf)) AS failure, " 
               "SUM(proc_ponc) AS sum_ponc, " 
               "SUM(proc_poc) AS sum_poc, " 
               "SUM(proc_efc) AS sum_efc, "  
               "(SUM(proc_poc) + SUM(proc_ponc)) + SUM(proc_efc) AS tot_cost " 
               "FROM vw_proc_run_sum "
               "WHERE emp_id = %s "
               "GROUP BY proc_step_id "
               "ORDER BY proc_id, proc_seq", (authenticateUser))
        operatorCosts = cursor.fetchall()
        
        cursor.execute("SELECT DISTINCTROW proc_nm, proc_desc, proc_step_nm, proc_step_seq, proc_step_desc, proc_step_owner, "
                        "proc_step_status, proc_step_poc, proc_step_ponc, "
                       "proc_step_efc "
                       "FROM  map_person_proc_step "
                       "INNER JOIN vw_processes ON (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
                       "WHERE emp_id = 17")
        processcost = cursor.fetchall()
             
        conn.close()
        '''
        This a way of sending arguments to another area
        #query = ("SELECT * from person WHERE google_user_id ='" + str(authenticateUser) + "'")
        query = "SELECT * from person WHERE google_user_id = "
        condition1 = authenticateUser
        summary8 = database.query(query, condition1)
        '''
               
        template_values = {'summaryByProcess': summaryByProcess, 'summaryByCase': summaryByCase, 'orgProcesses' : orgProcesses, 
                           'consequencesAndAdjustments': consequencesAndAdjustments, 'authenticateUser': authenticateUser, 'notes': notes, 
                           'operatorCosts': operatorCosts, 'processcost': processcost, 'featureList': featureList}
        template = jinja2_env.get_template('measureOperatorPerformance.html')
        self.response.out.write(template.render(template_values))
        
class OwnerMeasurePerformance(webapp2.RequestHandler):
    def get(self):
        
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        memcacheProcesses = database.memcacheProcesses(self)
        user = database.gaeSessionUser()
        emp_id = user[0]['emp_id']
        google_user_id = user[0]['google_user_id']
        userName = user[0]['first_nm'] + user[0]['last_nm']
        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE proc_id = 14 OR proc_id = 15 "
                       "GROUP BY proc_step_id "
                       "ORDER BY proc_nm, proc_seq, case_nm")    
        orgProcesses = cursor.fetchall() #Individual "local" processes are not included in this summary. 
        
        cursor.execute("SELECT proc_id, proc_nm, proc_step_id, proc_step_nm, proc_seq, case_id, case_nm, instance_key, emp_id, "
                       "ROUND(SUM(proc_step_conf)/COUNT(proc_step_id)*100) AS conf_summary, SUM(proc_step_conf) AS proc_success, COUNT(proc_step_id) AS proc_step_total "
                       "FROM vw_proc_run_sum "
                       "WHERE proc_step_owner = %s"
                       "GROUP BY proc_step_id "
                       "ORDER BY proc_nm, proc_seq, case_nm", (authenticateUser))    
        ownerProcesses = cursor.fetchall() #Processes by owner
                
        
        cursor.execute("SELECT proc_nm, proc_step_nm, case_nm, instance_key, proc_run_start_tm, "
                       "proc_conseq, proc_innovation, emp_id, perf_stnd_notes_1, perf_stnd_notes_2, perf_stnd_notes_3 "
                       "FROM vw_proc_run_sum "
                       "WHERE proc_step_owner = %s AND "
                       "(proc_conseq != ' ' OR not null "
                       "OR proc_innovation != ' '  OR not null "
                       "OR perf_stnd_notes_1 != ' '  OR not null "
                       "OR perf_stnd_notes_2 != ' '  OR not null "
                       "OR perf_stnd_notes_3 != ' '  OR not null) "
                       "ORDER BY proc_nm, proc_step_nm, instance_key ", (authenticateUser))               
        consequencesAndAdjustments = list(cursor.fetchall())
        
        cursor.execute("SELECT proc_run_start_tm, proc_nm, proc_seq, proc_step_nm, case_nm, instance_key, emp_id, "
               "COUNT(proc_step_conf) AS tot_ops, SUM(proc_step_conf) AS tot_success, " 
               "(COUNT(proc_step_conf) - SUM(proc_step_conf)) AS failure, " 
               "SUM(proc_ponc) AS sum_ponc, " 
               "SUM(proc_poc) AS sum_poc, " 
               "SUM(proc_efc) AS sum_efc, "  
               "(SUM(proc_poc) + SUM(proc_ponc)) + SUM(proc_efc) AS tot_cost " 
               "FROM vw_proc_run_sum "
               "WHERE proc_step_owner = %s "
               "GROUP BY proc_step_id "
               "ORDER BY proc_id, proc_seq", (authenticateUser))
        operatorCosts = cursor.fetchall() # Operator costs for processes by owner
        
        cursor.execute("SELECT DISTINCTROW proc_nm, proc_desc, proc_step_nm, proc_step_seq, proc_step_desc, proc_step_owner, "
                        "proc_step_status, proc_step_poc, proc_step_ponc, "
                       "proc_step_efc "
                       "FROM  map_person_proc_step "
                       "INNER JOIN vw_processes ON (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
                       "WHERE proc_step_owner = %s", (authenticateUser))
        processcost = cursor.fetchall()
             
        conn.close()
        
        template_values = {'orgProcesses': orgProcesses, 'ownerProcesses': ownerProcesses, 'consequencesAndAdjustments': consequencesAndAdjustments, 
                           'authenticateUser': authenticateUser, 'operatorCosts': operatorCosts, 
                           'processcost': processcost, 'featureList': featureList}
        template = jinja2_env.get_template('measureOwnerProcesses.html')
        self.response.out.write(template.render(template_values))
               