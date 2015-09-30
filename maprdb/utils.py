import datetime
import logging
from functools import wraps
import jpype


logger = logging.getLogger(__name__)


class MapRDBError(Exception):
    pass


def is_based_on_class(java_class, class_name_to_find):
    if java_class == None:
        return False

    if java_class.getName() == class_name_to_find or is_based_on_class(java_class.getSuperclass(), class_name_to_find):
        return True

    for implemented_interface in java_class.getBaseInterfaces():
        if is_based_on_class(implemented_interface, class_name_to_find):
            return True


def java_to_python_cast(value):
    """
    Converts java object to corresponding python value
    :param value: java object
    :returns: corresponding python value
    """
    java_class = value.__javaclass__ if hasattr(value,'__javaclass__') else None

    if is_based_on_class(java_class,'java.lang.Number'):
        return value.value
    elif is_based_on_class(java_class,'java.util.Date'):
        return datetime.datetime(1900 + value.getYear(), 1 + value.getMonth(), \
                                 value.getDate(), value.getHours(), \
                                 value.getMinutes(), value.getSeconds(), int(value.getNanos()/1000))
    elif is_based_on_class(java_class, 'java.util.List'):
        new_value = []
        it = value.iterator()
        while it.hasNext():
            new_value.append(java_to_python_cast(it.next()))
        return new_value
    elif is_based_on_class(java_class, 'java.util.Map'):
        new_value = {}
        it = value.keySet().iterator()

        while it.hasNext():
            k = java_to_python_cast(it.next())
            v = java_to_python_cast(value.get(k))
            new_value[k] = v
        return new_value

    return value


def python_to_java_cast(value):
    """
    Converts python value to corresponding java object
    :param value: python value
    :returns: corresponding java object
    """
    if '_get_java_object' in dir(value):
        return value._get_java_object()
    elif isinstance(value, (tuple, list)):
        jlist = jpype.java.util.ArrayList()
        for value_item in value:
            jlist.add(python_to_java_cast(value_item))
        return jlist
    elif isinstance(value, (dict,)):
        jmap = jpype.java.util.HashMap()
        for k,v in value.items():
            jmap.put(python_to_java_cast(k), python_to_java_cast(v))
        return jmap
    elif isinstance(value, datetime.datetime):
        time = jpype.java.sql.Timestamp(value.year - 1900, value.month - 1, value.day,
                                        value.hour, value.minute, value.second, 1000*value.microsecond)
        return time
    elif isinstance(value, datetime.date):
        date = jpype.java.sql.Date(value.year - 1900, value.month, value.day)
        return date
    elif isinstance(value, datetime.time):
        time = jpype.java.sql.Time(value.hour, value.minute, value.second)
        return time

    return value


def handle_java_exceptions(f):
    """
    Decorator for that wraps all Java exceptions to MapRDBError
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
        except jpype.JavaException as e:
            logger.debug(e.stacktrace())
            raise MapRDBError(str(e)) from e
        except RuntimeError as e:
            if "No matching overloads found" in str(e):
                raise TypeError(str(e))
            raise e

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
            if cls.__args != (args, kwargs):
                logger.warn("Cannot change parameters of connection.")
            logger.warn("Only one connection can be opened, "
                        "previously created connection will be used.")

        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        cls.__args = args, kwargs
        return cls.instance
