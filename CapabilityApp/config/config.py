#    Centralised configuration
import cgi
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
import os
import datetime
import time
from google.appengine.api import rdbms
import MySQLdb, MySQLdb.cursors
'''
Configure
1. Change from Local to the appropriate CLOUD SQL instance
2. Change the password
3. Update the Yaml File: 
Version 1 for production, or 2 for dev
'''
'''
def get_connection(): #Database Connections: Local
    return rdbms.connect(instance='MySQL56', 
                         host='127.0.0.1', #'localhost' 
                         port=3306, 
                         database='capability', 
                         user='root', 
                         password='cDnfom100!', #coldDaring
                         charset='utf8', 
                         use_unicode = True, 
                         cursorclass=MySQLdb.cursors.DictCursor)
'''
def get_connection(): #Database Connections: CLOUD
        return MySQLdb.connect(unix_socket='/cloudsql/' + 'pca-dev-capability:capability', 
                               db='capability', 
                               user='root', 
                               passwd= '5Ab$olutes', #5A$
                               charset='utf8', 
                               use_unicode = True, 
                               cursorclass=MySQLdb.cursors.DictCursor)

'''
def get_connection(): #USE FOR DEVELOPMENT BUT DEPLOY USING: Database Connections: CLOUD 
    #db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='guestbook', user='root')
    if (os.getenv('SERVER_SOFTWARE') and os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
        return MySQLdb.connect(unix_socket='/cloudsql/' + 'pca-dev-capability:capability', 
                               db='capability', 
                               user='root', 
                               passwd= '5Ab$olutes', #5A$
                               charset='utf8', 
                               use_unicode = True, 
                               cursorclass=MySQLdb.cursors.DictCursor)
    else:
        return MySQLdb.connect(host='127.0.0.1', 
                               port=3306, user='root', 
                               passwd='cDnfom100!', 
                               db='capability', 
                               charset='utf8', 
                               use_unicode = True, 
                               cursorclass=MySQLdb.cursors.DictCursor)
'''
# Tools
def UTCTime():
    rawNow = datetime.datetime.now()
    now = rawNow.isoformat()
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