import os
import maprdb

connection = None


def maprdb_connect():
    """
    Ensures that we connect to DB only once.
    :return: Connection object
    """
    global connection
    if not connection:
        connection = maprdb.connect(mapr_home=os.path.dirname(__file__))
    return connection
