# bulghur-capability-01: Little change 3
import os
#import cgi
#import logging
import webapp2
#import time
import jinja2
#import itertools

from google.appengine.api import rdbms
from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
from controllers import measure, operate, home, design, utilities
from config import config
template_path = os.path.join(os.path.dirname(__file__), 'templates')


#Jinja2 Environment Setup
jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
) 

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, database=config.DATABASE_NAME, user=config.USER_NAME, password=config.PASSWORD, charset='utf8')
   
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
    def get(self): # / 
        self.templateValues = {}
        self.templateValues["title"] = 'jQuery Ajax - It looks terrific Hilary'
        template = jinja2_env.get_template("base.html")
        self.response.out.write(template.render(self.templateValues))
 

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

#################################################            All Pages       ##############################################################
### these are temporary until the pages handlers are completely built, then destroy
        
class PlayGroundHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(jinja2_env.get_template('playground.html').render({}))
        
class LeftNavHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(jinja2_env.get_template('leftnav.html').render({}))
        
        
        
#################################################            HANDLERS         #############################################################
              
application = webapp.WSGIApplication(
    [
        ("/", home.MainHandler),
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
        ("/ajax", AjaxHandler)

    ],
    debug=True
    
)