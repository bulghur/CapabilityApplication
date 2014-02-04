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
from controllers import collaborate, design, home, measure, operate, utilities
from config import *

# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, 
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', use_unicode = True)    
                 
class DevelopCapability(webapp.RequestHandler):
    def get(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_run.proc_output_conf "
                       "FROM proc_run "
                       "inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                       "inner join process ON (process_step.proc_id = process.proc_id) ") 
        processSummary = cursor.fetchall()
        conn.close()
        
        template_values = {'processSummary': processSummary, }
        template = jinja2_env.get_template('index.html')
        self.response.out.write(template.render(template_values))    
           
###################################################################Ajax########################################################################

class AjaxHandler(webapp2.RequestHandler):
    def get(self): # /ajax 
        '''
        self.templateValues = {}
        self.templateValues["title"] = 'jQuery Ajax - It looks terrific Hilary'
        template = jinja2_env.get_template("base.html")
        self.response.out.write(template.render(self.templateValues))
        '''
        
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()

        proc_id = self.request.get("proc_id")
        
        cursor.execute("SELECT * FROM process_step") # WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()


        
        conn.close()
        
        title = 'jQuery Ajax: AjaxHandler() with Process Steps'
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'title': title, }
        template = jinja2_env.get_template('base.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO entries (guestname, content) '
                       'VALUES (%s, %s)',
                       (
                       self.request.get('guestname'),
                       self.request.get('content')
                       ))
        conn.commit()
        conn.close()
        
class jQueryJSON(webapp2.RequestHandler):
    '''
    From tutorial: altered to load data from the database
    Check the console object Array
    Question remains where I can pass this...
    Renders: jQuery.html
    # http://www.youtube.com/watch?v=XkddK0Rd7nA
    '''
    def get(self):
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proc_id, proc_nm FROM process")
        rows = cursor.fetchall()
        conn.close()

        rowArray_list = []
        for row in rows:
            t = (row)
            rowArray_list.append(t)

        data = rowArray_list   
        
        if self.request.get('fmt') == "json": 
            #data = {'name': 'bob', 'age': 55, 'name': 'sally', 'age': 45}
            self.response.out.headers['Content-Type'] = ('text/json')
            self.response.out.write(json.dumps(data))
            return

        title = "jQuery JSON Tutorial-edited: jQueryJSON from SQL using ajaxjson.html"
        self.template_values = {'title': title, "t": t, 'rows': rows}
        template = jinja2_env.get_template('jQuery.html')
        self.response.out.write(template.render(self.template_values))
        
class ProcessDataJSON(webapp2.RequestHandler):
    '''
    Altered from tutorial
    Check the console object Array
    Load process data, create JSON, use in forms
    See jQueryJSON for the working tutorial
    Associated with:
    Renders: TBD
    '''
    def get(self):
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT proc_id, proc_nm, emp_id FROM process")
        rows = cursor.fetchall()
        conn.close()

        rowArray_list = []
        for row in rows:
            t = (row)
            rowArray_list.append(t)

        processJSON = json.dumps(rowArray_list)   
        
        if self.request.get('fmt') == "json": 
            #processJSON = {'name': 'bob', 'age': 55, 'name': 'sally', 'age': 45}
            self.response.out.headers['Content-Type'] = ('text/json')
            self.response.out.write(processJSON)
            return

        title = "jQuery JSON Tutorial: ProcessDataJSON()"
        self.template_values = {'title': title}
        template = jinja2_env.get_template('operateprocess.html')
        self.response.out.write(template.render(self.template_values))
        
class Comment(db.Model):
    '''
    Needed for AjaxJSON to post to the db 
    Creates the Entity Comment to store the KV pairs
    '''
    proc_id = db.StringProperty() # can be string list property
    proc_step_id = db.StringProperty() # can be string list property

class AjaxJSON(webapp2.RequestHandler):
    '''
    From tutorial: http://www.youtube.com/watch?v=cDN-sFM6ack
    Edit for DB Process to 
    Check the console object Array
    Load process loads JSON data on to page and ddb  
    Associated with: ajaxjson.html, scirptjson.js
    '''
    
    def get(self):
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        proc_id = self.request.get("proc_id")
        
        cursor.execute("SELECT * FROM process_step") # WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()

        conn.close()
        
        title = 'jQuery Ajax/JSON: From AjaxJSON() in main.py, def get'
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'title': title, }
        template = jinja2_env.get_template('ajaxjson.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        

        proc_id = self.request.get('text')    
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM process_step WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()

        self.response.out.write(ddb_proc_step)   

#################################################            All Pages       ##############################################################
### these are temporary until the pages handlers are completely built, then destroy
class ProcessModelHandler(webapp.RequestHandler):
    # sourced from http://code-tricks.com/create-a-simple-html5-tabs-using-jquery/
    def get(self):
        self.response.out.write(jinja2_env.get_template('processmodel.html').render({}))        

class PlayGroundHandler(webapp.RequestHandler):
    def get(self):
        
        authenticateUser = users.get_current_user()
        authenticateUser = str(authenticateUser)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT proc_id, proc_nm, proc_step_id, proc_step_seq, proc_step_nm "
                       "FROM vw_processes "
                       "WHERE proc_step_status = 'active' OR proc_step_owner = %s "
                       "ORDER BY proc_id, proc_step_seq", (authenticateUser))
        processmenu = cursor.fetchall()
        conn.close()
        
        template_values = {"processmenu": processmenu, }
        template = jinja2_env.get_template('playground.html')
        self.response.out.write(template.render(template_values))
        
class LeftNavHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("jinja2_env.get_template('leftnav.html').render({})")
   
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


                        
            conn = get_connection()
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
          
class MemcacheTest(webapp2.RequestHandler):

    def queryNavBuilder(self): # this is the query
        authenticateUser = str(users.get_current_user())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT app_feat_cat_0, app_feat_0, app_feat_1, app_feat_2, app_feat_type, app_feat_display_index "
                               "FROM map_person_to_feature "
                               "INNER JOIN app_feature ON (map_person_to_feature.app_feat_cat_id = app_feature.app_feat_cat_id) "
                               "INNER JOIN person ON (map_person_to_feature.emp_id = person.emp_id) "
                               "WHERE person.google_user_id = %s AND app_feat_active = 1 "
                               "ORDER BY app_feat_display_index", (authenticateUser)) 
        navList = cursor.fetchall()
        conn.close()
        return navList

    def memcacheNavBuilder(self): #if the Memcache is empty, load it with the query data
        client = memcache.Client()
        featureList = client.get('navList')
        
        if featureList is not None:
            pass
        else:
            featureList = self.queryNavBuilder()
            client.add('navList', featureList, 120)
        
        return featureList

    
    def get(self):
        generatedData = self.queryNavBuilder()
        memcacheData = self.memcacheNavBuilder()
        
        template_values = {'generatedData': generatedData, 'memcacheData': memcacheData}
        template = jinja2_env.get_template('memcache.html')
        self.response.out.write(template.render(template_values))
         
application = webapp.WSGIApplication(
    [
        ('/', Authenticate),
        ('/Memcache', MemcacheTest),
        ("/permissions", Permissions),
        ("/MainHandler", home.MainHandler),
        ("/YourProfile", collaborate.YourProfile),
        ("/ProcessModel", ProcessModelHandler),
        ("/OperateProcess", operate.OperateProcess), 
        ("/CreateInstance", operate.CreateInstance),
        ("/postProcessRun", operate.PostProcessRun),
        ("/AssessPerformance", operate.AssessPerformance),
        ("/PostProcessAssessment", operate.PostProcessAssessment),
        ("/CreateCase", operate.CreateCase),
        ("/MeasurePerformance", measure.MeasurePerformance),
        ("/PoncCalulator", measure.PoncCalulator),
        ("/postProcessSteps", design.PostProcessStep),
        ("/DevelopCapability", utilities.DevelopCapability),
        ("/utilities", utilities.UtilityHandler),
        ("/postprocess", utilities.PostProcess),
        ("/postprocessstep", utilities.PostProcessStep),
        ("/postrequirement", utilities.PostRequirement),
        ("/postperson", utilities.PostPerson),
        ("/playground", PlayGroundHandler),
        ("/leftnav", LeftNavHandler),
        ("/ajax", AjaxHandler),
        ("/ajaxjson", AjaxJSON),
        ("/jQueryJSON", jQueryJSON)
        

    ],
    debug=True
    
)