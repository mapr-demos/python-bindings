import jpype
import logging
from multipledispatch import dispatch
from maprdb import Connection
from maprdb.utils import handle_java_exceptions, python_to_java_cast, MapRDBError


logger = logging.getLogger(__name__)


class Condition(object):
    """
    Python wrapper of com.mapr.db.Condition object.
    Supports fluent interface and shorthand interface.
    You can pass dict or list to constructor:
    >> c = Condition([{ "country": "China"}, {"age": 34}])
    >> c = Condition({"country": "China", "age": 34})

    List of conditions converts to OR clause
    Dict of conditions converts to AND clause
    """
    def __init__(self, initial=None):
        self._java_condition = None
        self._MapRDB = None
        self._initial = initial

    @property
    def java_condition(self):
        if self._java_condition is None:
            logger.debug("'Condition' Java object creation requested")
            self._create_condition()
        return self._java_condition

    @java_condition.setter
    def java_condition(self, value):
        self._java_condition = value

    @handle_java_exceptions
    def _create_condition(self):
        self._MapRDB = Connection.get_instance().MapRDB
        self.java_condition = self._MapRDB.newCondition()
        if self._initial:
            self._parse_condition(self._initial)

    @handle_java_exceptions
    def _and(self):
        self.java_condition = getattr(self.java_condition, "and") ()
        return self

    @handle_java_exceptions
    def _or(self):
        self.java_condition = self.java_condition.or_()
        return self

    @handle_java_exceptions
    def _close(self):
        self.java_condition = self.java_condition.close()
        return self

    @handle_java_exceptions
    def _exists(self, name):
        self.java_condition = self.java_condition.exists(name)
        return self

    @handle_java_exceptions
    def _not_exists(self, name):
        self.java_condition = self.java_condition.notExists(name)
        return self

    @handle_java_exceptions
    def _is(self, field, condition, value):
        value = python_to_java_cast(value)
        self.java_condition = self.java_condition.is_(field, condition, value)
        return self

    @dispatch(dict)
    def _parse_condition(self, initial):
        """
        Parse dictionary, which is alias for AND condition
        """
        if len(initial) > 1:
            self._and()
        for key,value in initial.items():
            operator, value = self._parse_operator_and_value(value)
            # ['LESS', 'LESS_OR_EQUAL', 'EQUAL', 'NOT_EQUAL', 'GREATER_OR_EQUAL', 'GREATER']
            if operator in ["$eq", "$equal", "="]:
                self._is(key, Op.EQUAL, value)
            elif operator in ["$ne", "$neq", "!="]:
                self._is(key, Op.NOT_EQUAL, value)
            elif operator in ["$lt", "$less", "<"]:
                self._is(key, Op.LESS, value)
            elif operator in ["$lte", "$le", "<="]:
                self._is(key, Op.LESS_OR_EQUAL, value)
            elif operator in ["$gt", "$greater", ">"]:
                self._is(key, Op.GREATER, value)
            elif operator in ["$ge", "$gte", ">="]:
                self._is(key, Op.GREATER_OR_EQUAL, value)
            elif operator in ["$between"]:
                self._between(key, value)
            elif operator in ["$in"]:
                self._in(key, value)
            elif operator in ["!$in"]:
                self._not_in(key, value)
            elif operator in ["$exists"]:
                if value:
                    self._exists(key)
                else:
                    self._not_exists(key)
            elif operator in ["$like", "$matches"]:
                raise NotImplementedError("$like is not implemented")
            elif operator in ["!$like", "!$matches"]:
                raise NotImplementedError("!$like is not implemented")

            else:
                raise MapRDBError("Unknown operator '{}'".format(operator))
        if len(initial) > 1:
            self._close()

    def _not_in(self, key, in_list):
        if not isinstance(in_list, list):
            raise MapRDBError("For $in operator value should be list")
        self._and()
        for item in in_list:
            self._is(key, Op.NOT_EQUAL, item)
        self._close()

    def _in(self, key, in_list):
        if not isinstance(in_list, list):
            raise MapRDBError("For $in operator value should be list")
        self._or()
        for item in in_list:
            self._is(key, Op.EQUAL, item)
        self._close()

    def _between(self, key, pair):
        if not isinstance(pair, list) or len(pair) != 2:
            raise MapRDBError("For $between operator value should be list of two elements")
        self._and()
        self._is(key, Op.GREATER_OR_EQUAL, pair[0])
        self._is(key, Op.LESS_OR_EQUAL, pair[1])
        self._close()

    @dispatch(list)
    def _parse_condition(self, initial):
        """
        Parse list, which is alias for OR condition
        """
        if len(initial) > 1:
            self._or()
        for condition in initial:
            self._parse_condition(condition)
        if len(initial) > 1:
            self._close()

    def _parse_operator_and_value(self, value):
        if isinstance(value, dict):
            operator = list(value.keys())[0]
            cond_value = value[operator]
        else:
            operator = "="
            cond_value = value
        return operator, cond_value
    
    def _get_java_object(self):
        return self.java_condition



class OperationsType(type):
    """
    Metaclass for Op object.
    Allows to call override __getattr__ for static fields.
    """
    _Op = None

    def _get_Op(cls):
        """
        Enumeration with all operation types
        """
        if not cls._Op:
            cls._Op = jpype.JClass("com.mapr.db.Condition$Op")
        return cls._Op

    def all_values(cls):
        if not jpype.isJVMStarted():
            raise MapRDBError("Open connection first")
        return [v.toString() for v in cls._get_Op().values()]

    def __getattr__(cls, item):
        if not jpype.isJVMStarted():
            raise AttributeError("Open connection first")
        try:
            return cls._get_Op().valueOf(item)
        except jpype.JavaException as e:
            if e.javaClass().__name__ == "java.lang.IllegalArgumentException":
                raise AttributeError("No such enum constant {}".format(item))
            else:
                raise e

class Op(object, metaclass=OperationsType):
    """
    Operations enumeration. You can access required item like Op.GREATER_OR_EQUAL
    >> c = Condition(). \
            _is("dob", Op.GREATER_OR_EQUAL, datetime.date(year=1980, month=1, day=1))
    Wrapper for com.mapr.db.Condition$Op
    """
    pass
