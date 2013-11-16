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
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config
from model import sql

template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))


def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')

def sessionVariables(self):
## Session Variables
    proc_id = 5
    JSONproc_id = self.response.out.write(json.dumps(proc_id))

class OandMProcessData(object):
    '''
    Purpose: Runs query to get processes
    '''
    
    def __init__(self):
              
        conn = get_connection()
        cursor = conn.cursor()      
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        self.dataProcess = cursor.fetchall()
        
        conn.close()
        
OandMProcessData = OandMProcessData()
