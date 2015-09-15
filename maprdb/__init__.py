"""
MapRDB Python API
"""

import glob
import os


JARS_LIST = glob.glob(os.path.join(os.path.dirname(__file__), "dependency", "*.jar"))

from maprdb.connection import Connection
from .connection import connect
from .conditions import Condition
from .mutation import Mutation
from .tables import Table
