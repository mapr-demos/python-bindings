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
        [string, list<Object>/dict<String,Object>/int/float]
        """
        result = self.java_mutation.set(field_name, python_to_java_cast(value))
        return Mutation(result)
    
    @handle_java_exceptions
    def append(self, field_name, value):
        """
        [string, list<Object>]
        """
        result = self.java_mutation.append(field_name, python_to_java_cast(value))
        return Mutation(result)
    
    @handle_java_exceptions
    def increment(self, field_name, value):
        """
        [string, int/float]
        """
        result = self.java_mutation.increment(field_name, value)
        return Mutation(result)
    
    @handle_java_exceptions
    def decrement(self, field_name, value):
        """
        [string, int/float]
        """
        result = self.java_mutation.increment(field_name, -1*value)
        return Mutation(result)
    
    @handle_java_exceptions
    def delete(self, field_name):
        """
        [string]
        """
        result = self.java_mutation.delete(field_name)
        return Mutation(result)
        
    @handle_java_exceptions
    def build(self):
        result = self.java_mutation.build()
        return Mutation(result)
      
    def _get_java_object(self):
        return self.java_mutation