import os
import logging

import jpype
from jpype import startJVM, getDefaultJVMPath, isJVMStarted

from maprdb import JARS_LIST
from maprdb.tables import Table
from maprdb.utils import Singleton, MapRDBError, handle_java_exceptions

logger = logging.getLogger(__name__)


def connect(mapr_home=None, **connection_info):
    """
    Connect to MapRDB
    :return: Connection object
    """
    info = connection_info.copy()
    if mapr_home:
        info.update({"mapr.home.dir": mapr_home})
    return Connection.get_instance(conn_info=info)


class Connection(object, metaclass=Singleton):
    """
    MapRDB Connection business delegate.
    """
    def __init__(self, conn_info, options=None):
        if not options:
            options = {}
        self.options = options
        self.connection_info = conn_info

        self._open()
        self.MapRDB = jpype.JClass("com.mapr.db.MapRDB")

    @handle_java_exceptions
    def _open(self):
        if isJVMStarted():
            raise MapRDBError("JVM is already started. Only one connection can be opened.")
        logger.info("Starting JVM")

        startJVM(getDefaultJVMPath(), *self._jvm_args())

    def _jvm_args(self):
        args = ["-Djava.class.path={}".format(os.pathsep.join(JARS_LIST))]
        args += ["-D{}={}".format(key, value) for key,value in self.connection_info.items()]
        return args

    @handle_java_exceptions
    def get(self, name):
        j_table = self.MapRDB.getTable(name)
        return Table(j_table)

    @handle_java_exceptions
    def create(self, name):
        j_table = self.MapRDB.createTable(name)
        return Table(j_table)

    @handle_java_exceptions
    def delete(self, name):
        self.MapRDB.deleteTable(name)

    @handle_java_exceptions
    def exists(self, name):
        return self.MapRDB.tableExists(name) == 1

    def set_options(self, **options):
        self.options.update(options)

    def get_options(self, **options):
        return self.options
