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

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE,
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', 
                         use_unicode = True,
                         )

class YourProfile(webapp.RequestHandler):
    '''
    Queries on people 
    '''
    def get(self):

        conn = get_connection()
        cursor = conn.cursor()
        
        authenticateUser = str(users.get_current_user()) 
        
        cursor.execute("SELECT * FROM person WHERE google_user_id = %s", (authenticateUser))        
        yourprofile = cursor.fetchall()     
        
        cursor.execute("SELECT * FROM person")   
                      
        yourteam = cursor.fetchall()
             
        conn.close()
               
        template_values = {'yourprofile': yourprofile, 'yourteam': yourteam}
        template = jinja2_env.get_template('collaborate.html')
        self.response.out.write(template.render(template_values))
 
        
            