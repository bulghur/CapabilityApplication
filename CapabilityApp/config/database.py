import config

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

def memcacheNavBuilder(): #if the Memcache is empty, load it with the query data
    client = memcache.Client()
    navList = client.get('navList')
    if navList is not None:
        pass
    else:
        navList = queryNavBuilder()
        client.add('navList', navList, 3600)

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

def memcacheProcessMenu(): #if the Memcache is empty, load it with the query data
    client = memcache.Client() 
       
    processmenu = client.get('processmenu')
    if processmenu is not None:
        pass
    else:
        processmenu = queryProcessMenu()
        client.add('processmenu', processmenu, 120) 
               
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
    
    
def memcacheActiveCase(): #if the Memcache is empty, load it with the query data
    client = memcache.Client() 
       
    ddb_active_case = client.get('ddb_active_case')
    if ddb_active_case is not None:
        pass
    else:
        ddb_active_case = queryActiveCase()
        client.add('ddb_active_case', ddb_active_case, 120) 
               
    return ddb_active_case

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