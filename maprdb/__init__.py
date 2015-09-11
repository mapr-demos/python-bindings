import glob
import os


JARS_LIST = glob.glob(os.path.join(os.path.dirname(__file__), "dependency", "*.jar"))

from .connection import connect
