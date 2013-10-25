import os
import config
import cgi
import logging
import time
import webapp2
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import config

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')


        
class DoCustomQueries():
    def query(self, sqlscript):
        conn = get_connection()
        cursor = conn.cursor()
                    
        cursor.execute(sqlscript)
        self.results = cursor.fetchall()
    
        conn.close()
'''
    def __init__(selfparams):
    '''
        