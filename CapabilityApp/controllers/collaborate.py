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

class CollaborationHandler(webapp.RequestHandler):
    '''
    This handler populates all the tabs with data and sets up the posts.  To do:  
    Move some data to memcache and gaesessions.  
    '''
    def get(self):        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user()) 
        user = database.gaeSessionUser()
        userName = user[0][1:5]
        emp_id = user[0][0]
        googleID = user[0][4]
        featureList = database.gaeSessionNavBuilder()
        processmenu = database.gaeSessionProcessMenu()
        
        cursor.execute("SELECT * FROM vw_processes WHERE proc_owner = %s ", (authenticateUser))        
        ownerProcesses = cursor.fetchall()     

        cursor.execute("SELECT DISTINCT vw_processes.proc_nm, vw_processes.proc_step_nm, vw_processes.proc_step_seq, vw_processes.proc_owner, "
                       "person.first_nm, person.last_nm, map_person_proc_step.status "
                       "FROM capability.map_person_proc_step "
                       "INNER JOIN vw_processes on (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
                       "INNER JOIN person on (map_person_proc_step.emp_id = person.emp_id) "
                       "WHERE map_person_proc_step.status = 1 AND map_person_proc_step.emp_id = %s ", (emp_id))      
        subscribedProcesses = cursor.fetchall()   
        
        cursor.execute("SELECT DISTINCT vw_processes.proc_nm, vw_processes.proc_step_nm, vw_processes.proc_step_seq, vw_processes.proc_owner, "
                       "person.first_nm, person.last_nm, map_person_proc_step.status "
                       "FROM capability.map_person_proc_step "
                       "INNER JOIN vw_processes on (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
                       "INNER JOIN person on (map_person_proc_step.emp_id = person.emp_id) "
                       "WHERE map_person_proc_step.status = 0 AND map_person_proc_step.emp_id = %s ", (emp_id))        
        requestedProcesses = cursor.fetchall()       
        
        cursor.execute("SELECT DISTINCT map_person_proc_step.map_person_proc_step_id, vw_processes.proc_nm, vw_processes.proc_step_nm, "
                       "person.first_nm, person.last_nm, map_person_proc_step.status "
                       "FROM map_person_proc_step "
                       "LEFT OUTER JOIN vw_processes on (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
                       "LEFT OUTER JOIN person on (map_person_proc_step.emp_id = person.emp_id) "
                       "WHERE map_person_proc_step.status = 0 AND map_person_proc_step.emp_id = %s "
                       "ORDER BY map_person_proc_step.map_person_proc_step_id ", (emp_id))        
        grantRequest = cursor.fetchall()    
 
        cursor.execute("SELECT DISTINCT proc_id, proc_nm, proc_step_id, proc_step_seq, proc_step_nm, proc_step_status "
                       "FROM vw_processes "
                       "WHERE (proc_step_id NOT IN (SELECT proc_step_id FROM map_person_proc_step where emp_id= %s )) "
                       "AND (vw_processes.proc_step_status = 'ZD Capable' OR vw_processes.proc_step_status = 'published') ", (emp_id))     
        availableProcesses = cursor.fetchall() 
                       
        cursor.execute("SELECT * FROM person")                 
        yourteam = cursor.fetchall()
             
        conn.close()
               
        template_values = {'authenticateUser': authenticateUser, 'featureList': featureList, 'processmenu': processmenu, 
                           'user': user, 'userName': userName, 'emp_id': emp_id, 'googleID': googleID, 
                           'ownerProcesses': ownerProcesses, 'subscribedProcesses': subscribedProcesses, 'yourteam': yourteam,
                           'requestedProcesses': requestedProcesses, 'grantRequest': grantRequest, 'availableProcesses': availableProcesses}
        template = jinja2_env.get_template('collaborate.html')
        self.response.out.write(template.render(template_values))

class PostPerson(webapp.RequestHandler):
    def post(self): # post to DB
        
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()  
        
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

        self.response.out.write(jinja2_env.get_template('collaborate.html').render({}))       
        
class YourProfile(webapp2.RequestHandler):
    '''
    Queries on people 
    '''
    def get(self):

        conn = config.get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user()) 
        featureList = database.gaeSessionNavBuilder()
        
        cursor.execute("SELECT * FROM person WHERE google_user_id = %s", (authenticateUser))        
        yourprofile = cursor.fetchall()     
        
        cursor.execute("SELECT * FROM person")   
                      
        yourteam = cursor.fetchall()
             
        conn.close()
               
        template_values = {'yourprofile': yourprofile, 'yourteam': yourteam}
        template = jinja2_env.get_template('collaborate.html')
        self.response.out.write(template.render(template_values))
        
class RequestSubscription(webapp.RequestHandler):
   def post(self):
        emp_id = self.request.get('emp_id')
        proc_step_id = self.request.get('proc_step_id')
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO map_person_proc_step (proc_step_id, emp_id, status) "
                       "VALUES(%s, %s, %s) ",
                       (
                        (proc_step_id),
                        (emp_id),
                        (0)
                        ))
        conn.commit()
        
        self.redirect("/CollaborationHandler")
        
class GrantSubscription(webapp.RequestHandler):
    '''
    This handler displays requested subscriptions for the Owner to grant.
    '''
    def post(self):
        map_person_proc_step_id = self.request.get('map_person_proc_step_id')
        status = self.request.get('status')
        
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE map_person_proc_step SET status = %s WHERE map_person_proc_step_id = %s ", (status, map_person_proc_step_id))
        conn.commit()
        
        self.redirect("/CollaborationHandler")
        
            