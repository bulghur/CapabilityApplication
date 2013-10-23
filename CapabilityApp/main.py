# bulghur-capability-01: Little change 3
import os
import webapp2
import jinja2
import logging
import string

from google.appengine.api import rdbms
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from controllers import measure, operate, home, design, utilities
from config import config
import unicodedata
# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')

class Authenticate(webapp2.RequestHandler):
    def get(self):
        authenticateUser = users.get_current_user()
        
        if authenticateUser: #Email == "paul.weber@philipcrosby.com":
            
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>) <li class="icn_edit_article"><a href="/permissions">Go to Main Page</a></li>' %
                        (authenticateUser.email(), users.create_logout_url("/")))
        else:
            greeting = ('<a href="%s">Sorry, you are not authorised to use this application</a>.' %
                        users.create_login_url("/"))

        self.response.out.write('<html><body>%s</body></html>' % greeting)
            
              
class DevelopCapability(webapp.RequestHandler):
    def get(self):
        sqlMeasureAll = "SELECT person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, SUM(proc_run.proc_output_conf)/COUNT(*) FROM proc_run inner join person ON (proc_run.emp_id = person.emp_id) inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) inner join process ON (process_step.proc_id = process.proc_id) WHERE proc_run.proc_run_status='C' AND person.emp_id = 1 GROUP BY proc_run.emp_id, proc_run.proc_req_id"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sqlMeasureAll)
        rows = cursor.fetchall()
        conn.close()
        
        template_values = {'rows': rows, }
        template = jinja2_env.get_template('developcapability.html')
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
        proc_id = self.request.get("proc_id")
        proc_step_id = self.request.get("proc_step_id")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()

        cursor.execute("SELECT * FROM process_step WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()

        cursor.execute("SELECT * FROM proc_req where proc_step_id=%s", (proc_step_id))
        ddb_requirement = cursor.fetchall()
        
        conn.close()
        
        title = 'jQuery Ajax - It looks terrific Hilary'
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'ddb_requirement': ddb_requirement, 'title': title, }
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


class Comment(db.Model):
    text = db.StringProperty
        
class AjaxJSON(webapp2.RequestHandler):
    def get(self):
        proc_id = self.request.get("proc_id")
        proc_step_id = self.request.get("proc_step_id")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()

        conn.close()
        
        title = 'jQuery Ajax/JSON'
        template_values = {'ddb_process': ddb_process, 'title': title, }
        template = jinja2_env.get_template('ajaxjson.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):

        proc_id = self.request.get("text")
        title = proc_id
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT proc_step_id, proc_step_nm FROM process_step WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()
        conn.close()
        
        self.response.out.write('<li>' + ddb_proc_step + '</li>')
        


        

        
        

#################################################            All Pages       ##############################################################
### these are temporary until the pages handlers are completely built, then destroy
        
class PlayGroundHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(jinja2_env.get_template('playground.html').render({}))
        
class LeftNavHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("jinja2_env.get_template('leftnav.html').render({})")
        
class Permissions(webapp.RequestHandler): #This is messy -- clean it up
        def get(self):
            authenticateUser = users.get_current_user()
            email = authenticateUser.email()
            

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM person WHERE email = %s', (email))
            person = cursor.fetchall()
            person1 = [str(person).encode('unicode-escape') for person in person]
            person2 = '["' + "(u'" + email + "'," + ')"]'  #HACK!!!



            if  email == "m4bulghur@gmail.com" or "paul.weber@philipcrosby.com" or "cheryl.salatino@philipcrosby.com" :
                conn = get_connection()
                cursor = conn.cursor()
                
                sqlScript = "SELECT proc_run.proc_req_id, person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm,SUM(proc_run.proc_output_conf)/COUNT(*), COUNT(*) FROM proc_run inner join person ON (proc_run.emp_id = person.emp_id) inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) inner join process ON (process_step.proc_id = process.proc_id) WHERE proc_run.proc_run_status='C' GROUP BY proc_run.emp_id, proc_run.proc_req_id"
                cursor.execute(sqlScript)
                rows = cursor.fetchall()
            
                sqlScript1 = "SELECT proc_nm, proc_step_nm, proc_step_desc FROM process inner join process_step ON (process_step.proc_id = process.proc_id)"
                cursor.execute(sqlScript1)
                processes = cursor.fetchall()
                
                cursor.execute("SELECT * FROM process ORDER by proc_nm")
                ddb_process = cursor.fetchall()
                
                conn.close()
            
                template_values = {"rows": rows, "processes": processes, "authenticateUser": authenticateUser, "person": person, "ddb_process": ddb_process, "person1": person1, "email": email, "person2": person2
                                   }
                template = jinja2_env.get_template('index.html')
                self.response.out.write(template.render(template_values))
                
            else:
                greeting = ('<a href="%s">Sorry, you are not authorised to use this application</a>.' %
                        users.create_login_url("/"))
                self.response.out.write('<html><body>%s</body></html>' % greeting)
  
        
        
#################################################            HANDLERS         #############################################################
              
application = webapp.WSGIApplication(
    [
        ('/', Authenticate),
        ("/permissions", Permissions),
        ("/mainhandler", home.MainHandler),
        ("/OperateProcess", operate.OperateProcess),
        ("/postProcessRun", operate.PostProcessRun),
        ("/SelectProcessStep", operate.SelectProcessStep),
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
        ("/ajaxjson", AjaxJSON)

    ],
    debug=True
    
)