# bulghur-capability-01
import os
import webapp2
import jinja2
import logging
import string
import json
import collections
import unicodedata
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from controllers import home, design, utilities
import config
import main

authenticateUser = users.get_current_user()


def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, 
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', use_unicode = True)            
              

class GrantAccess(webapp2.RequestHandler):
    '''
    This authenticates based on App Engine authentication with Google using a gmail user.
    See this: http://webapp-improved.appspot.com/tutorials/auth.html
    '''
        
    def get(self):
        authenticateUser = users.get_current_user()
        
        if authenticateUser:
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT google_user_id FROM person WHERE google_user_id = %s', (authenticateUser))
            person = cursor.fetchall()
            conn.close()
            '''
            TODO: Get the first name of the use and other user information, index to the get google_user_id,
            determine authorisations and then fill in the left nav with areas available to the users.  Finally, 
            turn the authenticate user into a user object in config used to determine all application  capabilities
            of the session.             
            '''
            person = str(person)
            authenticateUser = str(authenticateUser)
            person = person.replace("((u'", "")
            person = person.replace("',),)", "")

            
            if person == authenticateUser:
                

                greeting = ('Welcome authenticateUser: %s! person: %s <li class="icn_edit_article">(<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/permissions">Go to Main Page</a></li>' %
                (authenticateUser, person, users.create_logout_url("/")))
 
            else:
                greeting = ('<a href="%s">You are not authorised to use this application.  Please see the application viceroy</a>.' %
                        users.create_login_url("/"))
             
        else:
            greeting = ('<a href="%s">You need a Google account and must be added as a user by the application viceroy.</a>.' %
                    users.create_login_url("/"))

        self.response.out.write('<html><body>%s</body></html>' % greeting)