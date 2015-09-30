from maprdb.connection import Connection
from maprdb.utils import handle_java_exceptions, python_to_java_cast, MapRDBError


class Mutation(object):
    """
    Python wrapper of com.mapr.db.Mutation object.
    Supports fluent interface and shorthand interface.
    You can pass a list to constructor:

    >>> mutation = Mutation([
      {"some_number": {"$inc": 4}},
      {"some_list": {"$append": [1,2,3]}},
      {"some_string2": {"$append": "def"}},
      {"some_string": {"$delete": []}},
      {"some_float": {"$dec": 1.0}},
      {"some_new_field": {"$set": 123}},
    ]).build()

    as well as use a fluent interface:

    >>> mutation = Mutation().increment("some_number", 4).\
        append("some_list", [1,2,3]).\
        append("some_string2", "def").\
        delete("some_string").\
        decrement("some_float", 1.0).\
        set("some_new_field", 123).\
        build()
    """

    def __init__(self, mutation_dictionaries=None):
        self.java_mutation = Connection.get_instance().MapRDB.newMutation()

        if mutation_dictionaries:
            self._parse_mutation(mutation_dictionaries)

    def _get_function_by_operator_name(self, operator_name):
        try:
            return {
                '$set': self.set,
                '$setOrReplace': self.set_or_replace,
                '$inc': self.increment,
                '$dec': self.decrement,
                '$append': self.append,
                '$delete': self.delete
            }[operator_name]
        except KeyError:
            raise MapRDBError("Unknown operator '{}'".format(operator_name))

    def _parse_mutation(self, mutation_dictionaries):
        for mutation_dictionary in mutation_dictionaries:
            for field_name, field_mutation in mutation_dictionary.items():
                for operator_name, value in field_mutation.items():
                    self._get_function_by_operator_name(operator_name)(field_name, value)

    @handle_java_exceptions
    def set(self, field_name, value):
        """
        Sets the value of a field if no previous value exists.

        :param field_name: string value, which is a name of field to set.
        :param value: a list, dictionary, numeric or date value to set for the field.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.set(field_name, python_to_java_cast(value))
        return self

    @handle_java_exceptions
    def set_or_replace(self, field_name, value):
        """
        Sets the value of a field conditionally. If a previous value exists, it is overwritten.

        :param field_name: string value, which is a name of field to set.
        :param value: a list, dictionary, numeric or date value to set for the field.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.setOrReplace(field_name, python_to_java_cast(value))
        return self

    @handle_java_exceptions
    def append(self, field_name, value):
        """
        Appends the specified value to the specified field.

        :param field_name: string value, which is a name of field to set.
        :param value: a list or string value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.append(field_name, python_to_java_cast(value))
        return self

    @handle_java_exceptions
    def increment(self, field_name, value):
        """
        Increments the specified field by a specified value.

        :param field_name: string value, which is a name of field to increment.
        :param value: a numeric value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.increment(field_name, value)
        return self

    @handle_java_exceptions
    def decrement(self, field_name, value):
        """
        Decrements the specified field by a specified value.

        :param field_name: string value, which is a name of field to decrement.
        :param value: a numeric value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.increment(field_name, -1*value)
        return self

    @handle_java_exceptions
    def delete(self, field_name, value=None):
        """
        Deletes the specified field.

        :param field_name: string value, which is a name of field to delete.
        :return: maprdb.mutation.Mutation resulting instance
        """
        self.java_mutation = self.java_mutation.delete(field_name)
        return self

    @handle_java_exceptions
    def build(self):
        """
        Builds up the mutation, so it becomes usable, as an
        argument for other maprdb functions.
        """
        self.java_mutation = self.java_mutation.build()
        return self

    def _get_java_object(self):
        return self.java_mutation
