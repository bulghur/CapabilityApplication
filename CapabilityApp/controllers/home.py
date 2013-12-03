# bulghur-capability-01: Controls Home Page
import os
import cgi
import logging
import time
import jinja2
import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from config import database, config
template_path = os.path.join(os.path.dirname(__file__), '../templates')

#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8', use_unicode = True)

###################    COMMON    ##############################

authenticateUser = users.get_current_user()

class MainHandler(webapp.RequestHandler): 
        def get(self):
            authenticateUser = users.get_current_user()
            authenticateUser = str(authenticateUser)
            
            template_values = {"authenticateUser": authenticateUser}
            template = jinja2_env.get_template('index.html')
            self.response.out.write(template.render(template_values))