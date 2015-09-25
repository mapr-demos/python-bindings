import os
import logging

import jpype
from jpype import startJVM, getDefaultJVMPath, isJVMStarted

from maprdb import JARS_LIST
from maprdb.tables import Table
from maprdb.utils import Singleton, handle_java_exceptions

logger = logging.getLogger(__name__)


def connect(mapr_home=None, **connection_info):
    """
    Connect to MapRDB.
    :param mapr_home: -Dmapr.home.dir argument to JVM. Should point to the directory
    with 'conf/mapr-cluster.conf' file.
    :returns: Connection object
    """
    info = connection_info.copy()
    if mapr_home:
        info.update({"mapr.home.dir": mapr_home})
    return Connection.get_instance(conn_info=info)


class Connection(object, metaclass=Singleton):
    """
    MapRDB Connection object.
    Represents both connection to JVM and MapRDB class.
    Wrapper for com.mapr.db.MapRDB.
    """
    def __init__(self, conn_info, options=None):
        """
        Constructor of connection.
        :param conn_info: dictionary with JVM arguments
        :param options: map of options, not required [dict]
        """
        if not options:
            options = {}
        self.options = options
        self.connection_info = conn_info

        self._open()
        self.MapRDB = jpype.JClass("com.mapr.db.MapRDB")

    @handle_java_exceptions
    def _open(self):
        logger.info("Starting JVM")
        if isJVMStarted():
            logger.warn("JVM is already started. Only one connection can be opened,"
                        "previously created connection will be used.")
            return

        startJVM(getDefaultJVMPath(), *self._jvm_args())

    def _jvm_args(self):
        args = ["-Djava.class.path={}".format(os.pathsep.join(JARS_LIST))]
        args += ["-D{}={}".format(key, value) for key,value in self.connection_info.items()]
        return args

    @handle_java_exceptions
    def get(self, name):
        """
        Finds a table and returns a reference of type maprdb.Table.
        :param name: table name [str]
        :returns: table object [maprdb.Table]
        """
        j_table = self.MapRDB.getTable(name)
        return Table(j_table)

    @handle_java_exceptions
    def create(self, name):
        """
        Creates a table and returns a reference of type maprdb.Table.
        :param name: table name [str]
        :returns: table object [maprdb.Table]
        """
        j_table = self.MapRDB.createTable(name)
        return Table(j_table)

    @handle_java_exceptions
    def delete(self, name):
        """
        Deletes a table.
        :param name: table name [str]
        """
        self.MapRDB.deleteTable(name)

    @handle_java_exceptions
    def exists(self, name):
        """
        Returns a boolean value according to whether the table exists.
        :param name: table name [str]
        :returns: True if exists, False otherwise [bool]
        """
        return self.MapRDB.tableExists(name) == 1

    def setOptions(self, **options):
        """
        Sets the options specified in the map or return the state of all options.
        :param options: dictionary of changed options
        """
        self.options.update(options)

    def getOptions(self):
        """
        Returns current options.
        :returns: dictionary of options
        """
        return self.options
