import logging
from functools import wraps
import jpype

logger = logging.getLogger(__name__)


class MapRDBError(Exception):
    pass

def python_to_java_cast(value):
    if isinstance(value, (tuple, list)):
        jlist = jpype.java.util.ArrayList()
        for value_item in value:
            jlist.add(python_to_java_cast(value_item))
        return jlist
    elif isinstance(value, (dict,)):
        jmap = jpype.java.util.HashMap()
        for k,v in value.iteritems():
            jmap.put(python_to_java_cast(k), python_to_java_cast(v))
        return jmap
    return value

def handle_java_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
        except jpype.JavaException as e:
            logger.debug(e.stacktrace())
            raise MapRDBError(str(e)) from e

        return ret
    return wrapper

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None
        
    def __call__(cls, *args, **kwargs):
        raise Exception("{0} is singleton. Its instances should be accessed via {0}.get_instance() method".format(cls.__name__))
        
    def get_instance(cls, *args, **kwargs):
        if cls.instance and (args or kwargs):
            raise Exception("Cannot change parameters of singleton during runtime")
        
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance