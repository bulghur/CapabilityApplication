from google.appengine.api import rdbms
import config

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, 
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         harset='utf8', 
                         use_unicode = True)
dbResults = {}

class Database():

    def __init__(self):
           
        conn = get_connection()
        cursor = conn.cursor()      

        q = "SELECT * FROM process ORDER by proc_nm"
        cursor.execute(q)
        self.dbResults = cursor.fetchall()  
        
        conn.close()
        
        return self.dbResults

