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

def gaeSessionUser(): 
    session = get_current_session()
    user = session.get('user')
  
    if user is '':
        user = queryUser()
        session.set_quick('user', user)
    elif user is None:
        user = queryUser()
        session.set_quick('user', user)
    else:
        user

    return user

def queryAllUsers(): 
    #This generates a dict of all users
    conn = config.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM person") 
    allUsers = list(cursor.fetchall())
    conn.close()
    return allUsers

def gaeAllUsers(): 
    session = get_current_session()
    allUsers = session.get('allUsers')
  
    if allUsers is '':
        allUsers = queryAllUsers()
        session.set_quick('allUsers', allUsers)
    elif allUsers is None:
        allUsers = queryAllUsers()
        session.set_quick('allUsers', allUsers)
    else:
        allUsers

    return allUsers

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

def gaeSessionNavBuilder():
    session = get_current_session()
    navList = session.get('navList')
  
    if navList is '':
        navList = queryNavBuilder()
        session.set_quick('navList', navList)
    elif navList is None:
        navList = queryNavBuilder()
        session.set_quick('navList', navList)
    else:
        navList

    return navList 
    
def queryProcessMenu():     
    emp_id = gaeSessionUser()[0]['emp_id']
    
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

def gaeSessionProcessMenu():
    session = get_current_session()
    processmenu = session.get('processmenu')        

    if processmenu is '':
        processmenu = queryProcessMenu()
        session.set_quick('processmenu', processmenu)
    elif processmenu is None:
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
    elif ddb_active_case is None:
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

def cacheFilter(dataSource, constraint, searchColumn ):
    outerRow = {}
    innerRow = {}
    resultSet = {}
    columns = {}
    row = 0
    while row < len(dataSource):
        #if constraint in dataSource[row][searchColumn]:
        if dataSource[row][searchColumn] == constraint:
            columns = dataSource[0].keys()
            c = 0
            while c < len(columns):
                innerRow[columns[c]] = dataSource[row][columns[c]] 
                outerRow[row] = dict(innerRow)
                c += 1
            resultSet = outerRow.values()
        row += 1
    return resultSet
    

def query(query, condition1):  #this is the sample pattern
    #this is a test form of centralising a query
       
    conn = config.get_connection()
    cursor = conn.cursor()      

    cursor.execute(query + "'" + condition1 + "'" )
    dbResults = cursor.fetchall()  
    
    conn.close()
    
    return dbResults

######***********************    MEMCACH    ***********************######

def memcacheProcesses(self): #if the Memcache is empty, load it with the query data
    client = memcache.Client()
    allProcesses = client.get('allProcesses')
    
    if allProcesses is not None:
        pass
    else:
        #allProcesses = queryProcesses1(self)
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vw_processes") 
        allProcesses = cursor.fetchall()
        conn.close()
        return allProcesses
        client.add('allProcesses', allProcesses, 120)
    
    return allProcesses


'''
def sumProblemString(x, y):
    sum = x + y
    return 'The sum of {} and {} is {}.'.format(x, y, sum)
'''