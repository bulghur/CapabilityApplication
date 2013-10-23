#    Centralised configuration

import datetime

#Database Connections: LOCAL
CLOUDSQL_INSTANCE = 'MySQL56'
HOST = 'localhost'
DATABASE_NAME = 'capability'
USER_NAME = 'root'
PASSWORD = 'cdnfom1'

'''
#Database Connections: CLOUD
CLOUDSQL_INSTANCE = 'noble-freehold-326:learndb'
DATABASE_NAME = 'capability'
USER_NAME = 'root'
PASSWORD = ''
'''

def UTCTime():
    rawNow = datetime.datetime.now()
    now = rawNow.date().isoformat()
    return now
    