import os
import webapp2
import jinja2
import logging
import string
import json
import time
from gaesessions import get_current_session
from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from controllers import collaborate, design, home, measure, operate, utilities, playground, reviewprocess
from config import *

# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

class Authenticate(webapp2.RequestHandler):
    '''
This authenticates based on App Engine authentication with Google using a gmail user.
See this: http://webapp-improved.appspot.com/tutorials/auth.html

Fix authentication issues/bug by watching this: https://www.youtube.com/watch?v=yCS6cwYjl8o
'''
    def get(self):
        authenticateUser = str(users.get_current_user())
        featureList = database.gaeSessionNavBuilder()
        
        if authenticateUser:
            
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT google_user_id FROM person WHERE google_user_id = %s', (authenticateUser))
            person = cursor.fetchall()
            conn.close()
            '''
TODO: Get the first name of the use and other user information, index to the get google_user_id,
determine authorisations and then fill in the left nav with areas available to the users. Finally,
turn the authenticate user into a user object in config used to determine all application capabilities
of the session.
'''
            try:
                person = person[0]['google_user_id']
                person = str(person)
                authenticateUser = str(authenticateUser)
                person = person.replace("((u'", "")
                person = person.replace("',),)", "")
            
            except:
                person = "stranger"
                            
            if person == authenticateUser:
                # Clear the session cache
                session = get_current_session()
                session.set_quick('user', '')
                session.set_quick('navList', '')
                session.set_quick('processmenu', '')
                session.set_quick('ddb_active_case', '')
                session.set_quick('vw_processes', '')
    
                greeting = ('Welcome : %s! person: %s <li class="icn_edit_article">(<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/MainPageHandler">Go to Main Page</a></li>' %
                (authenticateUser, person, users.create_logout_url("/")))
             
            else:
                greeting = ('<a href="%s">Sorry Stranger, you are not authorised to use this application. The application administrator must grant you access via your PCA or Google credentials. If you have your log-on credentials, please click this to access the log-in screen.</a>' %
                        users.create_login_url("/"))
        else:
            greeting = ('<a href="%s">Sorry %s, you are not authorised to use this application</a>.' %
                    (person, users.create_login_url("/")))

        self.response.out.write('<html><body>%s</body></html>' % greeting)
        
class LogOut(webapp2.RequestHandler): 
    pass
    '''
    def get(self):    
        authenticateUser = str(users.get_current_user())  
        greeting = ('Welcome : %s! person: %s <li class="icn_edit_article">(<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/MainPageHandler">Go to Main Page</a></li>' %
                    (authenticateUser, users.create_logout_url("/logout")))
        self.response.out.write('<html><body>%s</body></html>' % greeting)
    '''
         
          
application = webapp.WSGIApplication(
    [
        ("/", Authenticate),
        ("/LogOut", LogOut),
        ('/CollaborationHandler', collaborate.CollaborationHandler),
        ("/YourProfile", collaborate.YourProfile),
        ("/GrantSubscription", collaborate.GrantSubscription),
        ("/postperson", collaborate.PostPerson),
        ("/RequestSubscription", collaborate.RequestSubscription),
        ("/GrantSubscription", collaborate.GrantSubscription),
        ("/MainPageHandler", home.MainPageHandler),
        ("/OperateProcess", operate.OperateProcess), 
        ("/CreateInstance", operate.CreateInstance),
        ("/PostInstance", operate.PostInstance),
        ("/AssessPerformance", operate.AssessPerformance),
        ("/PostProcessAssessment", operate.PostProcessAssessment),
        ("/PostConsequences", operate.PostConsequences),
        ("/CreateCase", operate.CreateCase),
        ("/ReviewCase", reviewprocess.ReviewCase),
        ("/SelectReviewCase", reviewprocess.SelectReviewCase),
        ("/EditInstance", reviewprocess.EditInstance),
        ("/MeasureOperatorPerformance", measure.MeasureOperatorPerformance),
        ("/OwnerMeasurePerformance", measure.OwnerMeasurePerformance),
        ("/postProcessSteps", design.PostProcessStep),
        ("/DevelopCapability", playground.DevelopCapability),
        ("/utilities", utilities.UtilityHandler),
        ("/postprocess", utilities.PostProcess),
        ("/postprocessstep", utilities.PostProcessStep),
        ("/postrequirement", utilities.PostRequirement),
        ("/ViewAssignments", utilities.ViewAssignments), 
        ("/ProcessModel", playground.ProcessModelHandler),
        ("/TestJinja2", playground.TestJinja2),
        ("/ajax", playground.AjaxHandler),
        ("/ajaxjson", playground.AjaxJSON),
        ("/jQueryJSON", playground.jQueryJSON)
        
    ],
    debug=True
    
)