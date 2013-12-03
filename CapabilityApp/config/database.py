from google.appengine.api import rdbms
import config

def get_connection():
    return rdbms.connect(instance=config.CLOUDSQL_INSTANCE, 
                         database=config.DATABASE_NAME, 
                         user=config.USER_NAME, 
                         password=config.PASSWORD, 
                         charset='utf8', 
                         use_unicode = True)
    
def query(query, condition1):
       
    conn = get_connection()
    cursor = conn.cursor()      

    cursor.execute(query + "'" + condition1 + "'" )
    dbResults = cursor.fetchall()  
    
    conn.close()
    
    return dbResults

'''
def sumProblemString(x, y):
    sum = x + y
    return 'The sum of {} and {} is {}.'.format(x, y, sum)
'''