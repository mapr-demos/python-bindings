import os
import maprdb

connection = None


def maprdb_connect():
    global connection
    if not connection:
        connection = maprdb.connect(mapr_home=os.path.dirname(__file__))
    return connection
