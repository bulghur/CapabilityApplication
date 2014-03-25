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
from google.appengine.ext import ndb

class Processes(ndb.Model): #please see: https://developers.google.com/appengine/docs/python/ndb/properties
    proc_nm = ndb.StringProperty()
    proc_desc = ndb.IntegerProperty()
    proc_owner = ndb.StringProperty()
    
row = Processes(proc_nm = 'hello', proc_desc = 12, proc_owner = 'Tom') 
row.put

# Paths and Jinja2
template_path = os.path.join(os.path.dirname(__file__), '../templates')

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path)
    )


class TestJinja2(webapp2.RequestHandler):
    def get(self):
        
        user = database.gaeSessionUser()
        userName = user[0]['first_nm'] + user[0]['last_nm']
        emp_id = user[0]['emp_id']
        google_id = user [0]['google_user_id']
        vw_processes = database.memcacheProcesses(self) 
        
        
        resultSet = database.cacheFilter(vw_processes, google_id, 'proc_step_owner')
        #resultSet = database.cacheFilter(resultSet, 14, 'proc_id')
 
        ''' 
        dataSource = vw_processes
        constraint = 14
        searchColumn = 'proc_id'
        outerRow = {}
        innerRow = {}
        resultSet = {}
        columns = {}
        row = 0
        while row < len(dataSource):
            if dataSource[row][searchColumn] == constraint:
                columns = dataSource[0].keys() #get column names
                c = 0
                while c < len(columns):
                    innerRow[columns[c]] = dataSource[row][columns[c]] 
                    outerRow[row] = dict(innerRow)
                    c += 1
                resultSet = outerRow.values()
            row += 1


        holdRow = {}
        innerRow = {}
        justValues = {}
        columns = {}
        row = 0
        while row < len(person):
            if 'paul.weber@philipcrosby.com' in person[row]['google_user_id']:
                innerRow['emp_id'] = person[row]['emp_id'] 
                innerRow['first_nm'] = person[row]['first_nm'] 
                innerRow['last_nm'] = person[row]['last_nm']
                innerRow['email'] = person[row]['email']  
                holdRow[row] = dict(innerRow)
                columns = person[0].keys()
                columnLen = len(columns)
                #get rid of the row/key references to yield a dictionary of values in the form of  [{'emp_id': 17L, 'last_nm': u'Weber', 'first_nm': u'Paul '}, {'emp_id': 34L, 'last_nm': u'The Toast', 'first_nm': u'Honey'}]
                justValues = holdRow.values()
            row += 1
        ''' 
        self.templateValues = {'userName': userName, 'emp_id': emp_id, 'google_id': google_id, 'resultSet': resultSet } 
        self.templateValues["title"] = 'This is from a second set of template values.'
        template = jinja2_env.get_template("TestJinja2.html")
        self.response.out.write(template.render(self.templateValues))
        
class DevelopCapability(webapp.RequestHandler):
    '''
    TODO: Move this to learn and use it to source videos and materials
    '''
    def get(self): 
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT person.last_nm, process.proc_nm, process_step.proc_step_nm, proc_req.proc_req_nm, "
                       "SUM(proc_run.proc_output_conf)/COUNT(*) "
                       "FROM proc_run "
                       "inner join person ON (proc_run.emp_id = person.emp_id) "
                       "inner join proc_req ON (proc_run.proc_req_id = proc_req.proc_req_id) "
                       "inner join process_step ON (proc_req.proc_step_id = process_step.proc_step_id) "
                       "inner join process ON (process_step.proc_id = process.proc_id) "
                       "WHERE proc_run.proc_run_status='C' AND person.emp_id = 1 "
                       "GROUP BY proc_run.emp_id, proc_run.proc_req_id")
        rows = cursor.fetchall()
        conn.close()
    
        
        template_values = {'rows': rows, }
        template = jinja2_env.get_template('developcapability.html')
        self.response.out.write(template.render(template_values)) 
        
class AjaxHandler(webapp2.RequestHandler):
    def get(self): # /ajax 

        self.templateValues = {}
        self.templateValues["title"] = 'jQuery Ajax - It looks terrific Hilary'
        template = jinja2_env.get_template("base.html")
        self.response.out.write(template.render(self.templateValues))

        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        sqlGetAllProcesses = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(sqlGetAllProcesses)
        ddb_process = cursor.fetchall()

        proc_id = self.request.get("proc_id")
        
        cursor.execute("SELECT * FROM process_step") # WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()


        
        conn.close()
        
        title = 'AjaxHandler(webapp2.RequestHandler):'
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'title': title, }
        template = jinja2_env.get_template('base.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        conn = config.get_connection()
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
        
        conn = config.get_connection()
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

        title = "jQueryJSON(webapp2.RequestHandler)"
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
        
        conn = config.get_connection()
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

        title = "class ProcessDataJSON(webapp2.RequestHandler)"
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
        
        conn = config.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM process ORDER by proc_nm")
        ddb_process = cursor.fetchall()
        
        proc_id = self.request.get("proc_id")
        
        cursor.execute("SELECT * FROM process_step") # WHERE process_step.proc_id=%s", (proc_id))
        ddb_proc_step = cursor.fetchall()

        conn.close()
        
        title = 'class AjaxJSON(webapp2.RequestHandler):'
        template_values = {'ddb_process': ddb_process, 'ddb_proc_step': ddb_proc_step, 'title': title, }
        template = jinja2_env.get_template('ajaxjson.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        

        proc_id = self.request.get('text')    
        
        conn = config.get_connection()
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
        
class MemcacheTest(webapp2.RequestHandler):

    def queryNavBuilder(self): # this is the query
        authenticateUser = str(users.get_current_user())
        conn = config.get_connection()
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