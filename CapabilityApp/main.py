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
        authenticateUser = users.get_current_user()
        authenticateUser = str(authenticateUser)
        
        if authenticateUser:
            
            conn = config.get_connection()
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
                # Clear the session cache
                session = get_current_session()
                session.set_quick('navList', '')
                session.set_quick('processmenu', '')
                session.set_quick('ddb_active_case', '')
    
                greeting = ('Welcome authenticateUser: %s! person: %s <li class="icn_edit_article">(<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/permissions">Go to Main Page</a></li>' %
                (authenticateUser, person, users.create_logout_url("/")))
             
            else:
                greeting = ('<a href="%s">Sorry Stranger, you are not authorised to use this application.  The application administrator must grant you access via your PCA or Google credentials.  If you have your log-on credentials, please click this to access the log-in screen.</a>' %
                        users.create_login_url("/"))
             
        else:
            greeting = ('<a href="%s">Sorry OUTSIDE, you are not authorised to use this application</a>.' %
                    users.create_login_url("/"))

        self.response.out.write('<html><body>%s</body></html>' % greeting)
        
class Permissions(webapp.RequestHandler): #This is messy coding -- clean it up
        def get(self):
            authenticateUser = users.get_current_user()
            authenticateUser = str(authenticateUser)
            featureList = database.gaeSessionNavBuilder()


                        
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT proc_id, proc_nm, SUM(proc_step_conf), COUNT(proc_id), SUM(proc_step_conf)/COUNT(proc_id) AS conformance_rate, "
                           "SUM(proc_ponc), SUM(proc_poc), SUM(proc_efc) "
                           "FROM `capability`.`vw_proc_run_sum` "
                           "WHERE proc_run_start_tm > (NOW() - INTERVAL 7 DAY)"
                           "GROUP BY proc_id") 
            activitySummary = cursor.fetchall()
            conn.close()
            
            template_values = {"authenticateUser": authenticateUser, 'activitySummary': activitySummary, 'featureList': featureList}
            template = jinja2_env.get_template('index.html')
            self.response.out.write(template.render(template_values))
          

         
application = webapp.WSGIApplication(
    [
        ('/', Authenticate),
        ("/permissions", Permissions),
        ("/YourProfile", collaborate.YourProfile),
        ("/OperateProcess", operate.OperateProcess), 
        ("/CreateInstance", operate.CreateInstance),
        ("/PostInstance", operate.PostInstance),
        ("/AssessPerformance", operate.AssessPerformance),
        ("/PostProcessAssessment", operate.PostProcessAssessment),
        ("/PostConsequences", operate.PostConsequences),
        ("/CreateCase", operate.CreateCase),
        ("/ReviewCase", reviewprocess.ReviewCase),
        ("/SelectReviewCase", reviewprocess.SelectReviewCase),
        ("/CaseReview", reviewprocess.CaseReview),
        ("/MeasurePerformance", measure.MeasurePerformance),
        ("/PoncCalulator", measure.PoncCalulator),
        ("/postProcessSteps", design.PostProcessStep),
        ("/DevelopCapability", utilities.DevelopCapability),
        ("/utilities", utilities.UtilityHandler),
        ("/postprocess", utilities.PostProcess),
        ("/postprocessstep", utilities.PostProcessStep),
        ("/postrequirement", utilities.PostRequirement),
        ("/postperson", utilities.PostPerson),
        ('/Memcache', playground.MemcacheTest),
        ("/playground", playground.PlayGroundHandler),
        ("/ProcessModel", playground.ProcessModelHandler),
        ("/leftnav", playground.LeftNavHandler),
        ("/ajax", playground.AjaxHandler),
        ("/ajaxjson", playground.AjaxJSON),
        ("/jQueryJSON", playground.jQueryJSON)
        
    ],
    debug=True
    
)