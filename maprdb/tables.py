from maprdb.utils import handle_java_exceptions, python_to_java_cast, MapRDBError, java_to_python_cast
from maprdb.document import Document
import copy

class Table(object):
    def __init__(self, java_table):
        self.java_table = java_table
    
    @handle_java_exceptions
    def find_by_id(self, key, list_of_column_names=None):
        """
        [string, list<string>]
        """
        java_document = self.java_table.findById(key)
        return Document.python_document_from_java(java_document, columns_to_retain=python_to_java_cast(list_of_column_names))
    
    def _find_by_java_document_stream(self, document_stream, columns=None):
        iterator = document_stream.iterator()

        while iterator.hasNext():
            yield Document(java_to_python_cast(iterator.next()), columns_to_retain=columns)
      
    @handle_java_exceptions
    def find(self, columns=None):
        """
        [list<string>]
        """
        document_stream = self.java_table.find()
        return self._find_by_java_document_stream(document_stream, columns=columns)

    
    def find_by_condition(self, condition, columns=None):
        """
        [condition, list<string>]
        """
        document_stream = self.java_table.find(python_to_java_cast(condition))
        return self._find_by_java_document_stream(document_stream, columns=columns)
    
    def _fill_document_key(self, doc, key=None):
        doc = copy.copy(doc)
        if '_id' not in doc:
            if key is None:
                raise MapRDBError("No key or _id property in document is specified.")
            doc['_id'] = key
        else:
            if not key is None:
                raise MapRDBError("Both key and _id property in document are specified.")
          
        return doc
    
    @handle_java_exceptions
    def insert(self, doc, key=None):
        """
        [document]
        """
        doc = self._fill_document_key(doc, key=key)
        self.java_table.insert(python_to_java_cast(doc))
        
    @handle_java_exceptions
    def insert_or_replace(self, doc, key=None):
        """
        [document, string]
        """
        doc = self._fill_document_key(doc, key=key)
        self.java_table.insertOrReplace(python_to_java_cast(doc))
    
    @handle_java_exceptions
    def update(self, key, mutation):
        """
        [string/list<string>,mutation]
        """
        keys_list = key if isinstance(key, (list,tuple)) else [key]
        
        for k in keys_list:
            self.java_table.update(k, python_to_java_cast(mutation))
    
    @handle_java_exceptions
    def update_all(self, values):
        """
        [dict<string,mutation>]
        """
        for k in values.keys():
            self.update(k, values[k])
    
    @handle_java_exceptions
    def delete(self, key):
        """
        [string]
        """
        self.java_table.delete(key)
    
    @handle_java_exceptions
    def flush(self):
        self.java_table.flush()