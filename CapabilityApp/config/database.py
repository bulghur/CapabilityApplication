import config
import os
import webapp2
import jinja2
from gaesessions import get_current_session
from google.appengine.api import rdbms
from google.appengine.api import users
from google.appengine.api import memcache 

# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    ) 
    

def queryUser(): 
    #This generates the leftnav features dependent on user rights on the application.
    authenticateUser = str(users.get_current_user())
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM person WHERE google_user_id = %s ", (authenticateUser)) 
    user = list(cursor.fetchall())
    conn.close()
    return user

def gaeSessionUser(): #if the Memcache is empty, load it with the query data
    session = get_current_session()
    user = session.get('user')
  
    if user is '':
        user = queryUser()
        session.set_quick('user', user)
    else:
        user

    return user

def queryNavBuilder(): 
    #This generates the leftnav features dependent on user rights on the application.
    authenticateUser = str(users.get_current_user())
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT app_feat_cat_0, app_feat_0, app_feat_1, app_feat_2, app_feat_type, app_feat_display_index "
                           "FROM map_person_to_feature "
                           "INNER JOIN app_feature ON (map_person_to_feature.app_feat_cat_id = app_feature.app_feat_cat_id) "
                           "INNER JOIN person ON (map_person_to_feature.emp_id = person.emp_id) "
                           "WHERE app_feat_active = 1 AND person.google_user_id = %s "
                           "ORDER BY app_feat_display_index", (authenticateUser)) 
    navList = cursor.fetchall()
    conn.close()
    return navList

def gaeSessionNavBuilder(): #if the Memcache is empty, load it with the query data
    session = get_current_session()
    navList = session.get('navList')
  
    if navList is '':
        navList = queryNavBuilder()
        session.set_quick('navList', navList)
    else:
        navList

    return navList 
    
def queryProcessMenu():     
    emp_id = gaeSessionUser()[0][0]
    conn = config.get_connection()
    cursor = conn.cursor() 

    cursor.execute("SELECT DISTINCT vw_processes.proc_id, vw_processes.proc_nm, vw_processes.proc_step_id, vw_processes.proc_step_seq, vw_processes.proc_step_nm "
           "FROM map_person_proc_step "
           "INNER JOIN vw_processes on (map_person_proc_step.proc_step_id = vw_processes.proc_step_id) "
           "INNER JOIN person on (map_person_proc_step.emp_id = person.emp_id) "
           "WHERE map_person_proc_step.emp_id = %s AND map_person_proc_step.status = 1 "
           "ORDER BY proc_id, proc_step_seq", (emp_id))
    processmenu = cursor.fetchall()
    
    conn.close()
    return processmenu  

def gaeSessionProcessMenu(): #if the Memcache is empty, load it with the query data
    session = get_current_session()
    processmenu = session.get('processmenu')        

    if processmenu is '':
        processmenu = queryProcessMenu()
        session.set_quick('processmenu', processmenu)
    else:
        processmenu
        
    return processmenu

def queryActiveCase():
    authenticateUser = str(users.get_current_user())
    conn = config.get_connection()
    cursor = conn.cursor() 
    
    cursor.execute("SELECT case_id, case_nm "
                   "FROM proc_case "
                   "WHERE status = 1 AND emp_id =%s", (authenticateUser))
    ddb_active_case = cursor.fetchall()
    conn.close()
    return ddb_active_case
    
    
def gaeSessionActiveCase():
    session = get_current_session()
    ddb_active_case = session.get('ddb_active_case')   
    
    if ddb_active_case is '':
        ddb_active_case = queryActiveCase()
        session.set_quick('ddb_active_case', ddb_active_case)
    else:
        ddb_active_case
               
    return ddb_active_case

def queryOpenOperations():
    authenticateUser = str(users.get_current_user())
    conn = config.get_connection()
    cursor = conn.cursor() 
    
    cursor.execute("SELECT case_id, case_nm "
                   "FROM proc_case "
                   "WHERE status = 1 AND emp_id =%s", (authenticateUser))
    openoperations = cursor.fetchall()
    conn.close()
    return openoperations
    
def gaeSessionOpenOperations():
    authenticateUser = str(users.get_current_user())
    session = get_current_session()
    openoperations = session.get('openoperations')
    
    if openoperations is None:
        conn = config.get_connection()
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM capability.vw_proc_run_sum WHERE proc_step_conf is null")
        openoperations = cursor.fetchall()
        conn.close()
        openoperations
    else:
        openoperations
               
    return openoperations

def query(query, condition1):  #this is the sample pattern
    #this is a test form of centralising a query
       
    conn = config.get_connection()
    cursor = conn.cursor()      

    cursor.execute(query + "'" + condition1 + "'" )
    dbResults = cursor.fetchall()  
    
    conn.close()
    
    return dbResults

class MemcacheTest(webapp2.RequestHandler):

    def queryBuilder(self): # this is the query
        authenticateUser = str(users.get_current_user())
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proc_nm, proc_desc, proc_owner, proc_status, proc_step_id, proc_step_seq, proc_step_nm, proc_step_desc, "
                       "proc_step_owner, proc_step_status, proc_req_id, proc_req_nm, proc_req_desc, "
                       "proc_req_seq, proc_req_status "
                       " FROM vw_processes "
                       "WHERE proc_id = 15") 
        memQuery = cursor.fetchall()
        conn.close()
        return memQuery

    def memcacheBuilder(self): #if the Memcache is empty, load it with the query data
        client = memcache.Client()
        memQuery = client.get('memQuery')
        
        if memQuery is not None:
            pass
        else:
            memQuery = self.queryBuilder()
            client.add('memQuery', memQuery, 120)
        
        return memQuery

    
    def get(self):
        memQuery = self.queryBuilder()
        generatedData = self.queryBuilder()
        memcacheData = self.memcacheBuilder()
        
        generatedList = list(generatedData)
        generatedList1 = memQuery[2][1]
        
        template_values = {'generatedData': generatedData, 'memcacheData': memcacheData, 'generatedList1': generatedList1}
        template = jinja2_env.get_template('memcache.html')
        self.response.out.write(template.render(template_values))
'''
def sumProblemString(x, y):
    sum = x + y
    return 'The sum of {} and {} is {}.'.format(x, y, sum)
'''