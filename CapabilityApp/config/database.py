import config
from gaesessions import get_current_session
from google.appengine.api import rdbms
from google.appengine.api import users
from google.appengine.api import memcache  
    
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
    authenticateUser = str(users.get_current_user())
    conn = config.get_connection()
    cursor = conn.cursor() 

    cursor.execute("SELECT DISTINCT proc_id, proc_nm, proc_step_id, proc_step_seq, proc_step_nm "
           "FROM vw_processes "
           "WHERE proc_step_status = 'active' OR proc_step_owner = %s "
           "ORDER BY proc_id, proc_step_seq", (authenticateUser))
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
'''
def sumProblemString(x, y):
    sum = x + y
    return 'The sum of {} and {} is {}.'.format(x, y, sum)
'''