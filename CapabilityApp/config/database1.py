##From: 
import MySQLdb
class Database:
    
    host = "localhost"
    user = "testuser"
    passwd = "testpass"
    de = "test"


    def __init__(self):
        self.connection = MySQLdb.connect(  host = self.host,
                                            uesr = self.user,
                                            passwd = self.passwd,
                                            db = self.db)
    
    def query(self, q):
        cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        cursor.execute(q)
        
        return cursor.fetchall()
    
    def __del__(self):
        self.connection.close()
        
if __name__ == "__main__":
    db = Database()
    
    q = "DELETE FROM testtable"
    
    db.query(q)
    
    q = """
    INSERT INTO testTable
    ('name', 'age')
    VALUES
    ('Paul','48')
    ('Hilary','53')  
    ('Sachie','18') 
    ('Ren','12')
    """
    db.query(q)
    
    q = """
    SELECT * FROM testTable
    WHERE age = 12
    """
    
    people = db.query(q)
    
    for person in people:
        print "found: %s " % person['name']
        
        ''' this returns a tuple, is it possible to use + to concatenate strings for args'''
    
    