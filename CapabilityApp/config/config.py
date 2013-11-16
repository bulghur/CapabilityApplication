#    Centralised configuration

import datetime
import time
from google.appengine.api import rdbms
#from controllers import measure

#Database Connections: LOCAL
CLOUDSQL_INSTANCE = 'MySQL56'
HOST = 'localhost'
DATABASE_NAME = 'capability'
USER_NAME = 'root'
PASSWORD = 'cdnfom1'

'''
#Database Connections: CLOUD
CLOUDSQL_INSTANCE = 'noble-freehold-326:learndb'
DATABASE_NAME = 'capability'
USER_NAME = 'root'
PASSWORD = ''
'''
def get_connection():
    return rdbms.connect(instance=CLOUDSQL_INSTANCE, database=DATABASE_NAME, user=USER_NAME, password=PASSWORD, charset='utf8', use_unicode = True)

# Tools
def UTCTime():
    rawNow = datetime.datetime.now()
    now = rawNow.date().isoformat()
    return now

def IDGenerator():
    idGenerator = time.time()
    return idGenerator
'''
class Test(object):
    
    self.proc_step_id = SelectProcessStep("proc_step_id")
    def querySelectProcessSteps(self):
            
        conn = get_connection()
        cursor = conn.cursor()
    
        cursor.execute("SELECT * FROM process_step WHERE process_step.proc_step_id=%s", (proc_step_id))
        ddb_proc_step = cursor.fetchall()
        
        conn.close()
        
        return ddb_proc_step  
        '''