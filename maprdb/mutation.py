from maprdb.connection import Connection
from maprdb.utils import handle_java_exceptions, python_to_java_cast

# by float I mean any fractional values
# by int any integral values
class Mutation(object):
    def __init__(self, java_mutation=None):
        self.java_mutation = java_mutation if java_mutation else Connection.get_instance().MapRDB.newMutation()
    
    @handle_java_exceptions
    def set(self, field_name, value):
        """
        Sets the specified value into the specified field.
        
        :param field_name: string value, which is a name of field to set.
        :param value: a list, dictionary, numeric or date value to set for the field.
        :return: maprdb.mutation.Mutation resulting instance
        """
        result = self.java_mutation.set(field_name, python_to_java_cast(value))
        return Mutation(result)
    
    @handle_java_exceptions
    def append(self, field_name, value):
        """
        Appends the specified value to the specified field.
        
        :param field_name: string value, which is a name of field to set.
        :param value: a list or string value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        result = self.java_mutation.append(field_name, python_to_java_cast(value))
        return Mutation(result)
    
    @handle_java_exceptions
    def increment(self, field_name, value):
        """
        Increments the specified field by a specified value.
        
        :param field_name: string value, which is a name of field to increment.
        :param value: a numeric value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        result = self.java_mutation.increment(field_name, value)
        return Mutation(result)
    
    @handle_java_exceptions
    def decrement(self, field_name, value):
        """
        Decrements the specified field by a specified value.
        
        :param field_name: string value, which is a name of field to decrement.
        :param value: a numeric value to append.
        :return: maprdb.mutation.Mutation resulting instance
        """
        result = self.java_mutation.increment(field_name, -1*value)
        return Mutation(result)
    
    @handle_java_exceptions
    def delete(self, field_name):
        """
        Deletes the specified field.
        
        :param field_name: string value, which is a name of field to delete.
        :return: maprdb.mutation.Mutation resulting instance
        """
        result = self.java_mutation.delete(field_name)
        return Mutation(result)
        
    @handle_java_exceptions
    def build(self):
        """
        Builds up the mutation, so it becomes usable, as an
        argument for other maprdb functions.
        """
        result = self.java_mutation.build()
        return Mutation(result)
      
    def _get_java_object(self):
        return self.java_mutation