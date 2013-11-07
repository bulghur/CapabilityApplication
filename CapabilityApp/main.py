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
from controllers import measure, operate, home, design, utilities
from config import config
from config import myhandler

# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 


def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8', use_unicode = True)            
              
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
        cursor.execute("SELECT proc_id, proc_nm, emp_id FROM process")
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
        
class PlayGroundHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(jinja2_env.get_template('playground.html').render({}))
        
class LeftNavHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("jinja2_env.get_template('leftnav.html').render({})")
   
class Authenticate(webapp2.RequestHandler):
    '''
This authenticates based on App Engine authentication with Google using a gmail user.
See this: http://webapp-improved.appspot.com/tutorials/auth.html
'''
    def get(self):
        authenticateUser = users.get_current_user()
        #email = authenticateUser.email
        nickname = '' #authenticateUser.nickname
        
        if authenticateUser:
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM person WHERE email = %s', (nickname))
            person = cursor.fetchall()
            conn.close()

            greeting = ('Welcome, %s! email: person: %s nickname: %s <li class="icn_edit_article">(<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/permissions">Go to Main Page</a></li>' %
                (authenticateUser.email(), person, nickname, users.create_logout_url("/")))
                      
        else:
            greeting = ('<a href="%s">Sorry, you are not authorised to use this application</a>.' %
                        users.create_login_url("/"))

        self.response.out.write('<html><body>%s</body></html>' % greeting)
        
class Permissions(webapp.RequestHandler): #This is messy -- clean it up
        def get(self):
            authenticateUser = users.get_current_user()
            email = authenticateUser.email()
            

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM person WHERE email = %s', (email))
            person = cursor.fetchall()
            conn.close()
            
            #person1 = [str(person).encode('unicode-escape') for person in person]
            #person2 = '["' + "(u'" + email + "'," + ')"]' #HACK!!!


            if (email == "m4bulghur@gmail.com" or "paul.weber@philipcrosby.com" or "cheryl.salatino@philipcrosby.com" or "govberg@gmail.com"):
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, SUM(proc_run.proc_output_conf)/COUNT(*), COUNT(proc_run.proc_output_conf) "
                               "FROM proc_run "
                               "INNER JOIN proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                               "INNER JOIN process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                               "INNER JOIN process ON (process_step.proc_id = process.proc_id) "
                               "GROUP BY process_step.proc_step_id, proc_req.proc_req_nm "
                               "ORDER BY process.proc_id, process_step.proc_seq") 
                processSummary = cursor.fetchall()
                conn.close()
                
                template_values = {"authenticateUser": authenticateUser, 'processSummary': processSummary}
                template = jinja2_env.get_template('index.html')
                self.response.out.write(template.render(template_values))
                
            else:
                greeting = ('<a href="%s">Sorry, you are not authorised to use this application</a>.' %
                        users.create_login_url("/"))
                self.response.out.write('<html><body>%s</body></html>' % greeting)
              
application = webapp.WSGIApplication(
    [
        ('/', Authenticate),
        ("/permissions", Permissions),
        ("/MainHandler", home.MainHandler),
        ("/OperateProcess", operate.OperateProcess),
        ('/SelectProcessStep', operate.SelectProcessStep), 
        ("/CreateInstance", operate.CreateInstance),
        ("/postProcessRun", operate.PostProcessRun),
        ("/CreateCase", operate.CreateCase),
        ("/MeasurePerformance", measure.MeasurePerformance),
        ("/postProcessSteps", design.PostProcessStep),
        ("/DevelopCapability", design.DevelopCapability),
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