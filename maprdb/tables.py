from maprdb.utils import handle_java_exceptions, python_to_java_cast, MapRDBError, java_to_python_cast
from maprdb.document import Document
import copy


class Table(object):
    """
    Python wrapper for com.mapr.db.Table object.

    This class is usually not instantiated by user,
    but returned from methods of maprdb.connection.Connection.get and maprdb.connection.Connection.create.
    """
    def __init__(self, java_table):
        self.java_table = java_table

    @handle_java_exceptions
    def find_by_id(self, key, columns=None):
        """
        Finds the specified record (document), possibly returning only a subset of available columns.
        If key is a list, return a list of results, one for each key value.
        Results (documents) are returned as a dict.

        :param key: string value, which is _id of the record to find.
        :param columns: list of strings, which
        specifies certain columns to select from the returned document.
        :returns: maprdb.document.Document class instance,
        which is the document found. If document was not found returns None.
        """
        java_document = self.java_table.findById(key, columns) if columns else self.java_table.findById(key)
        if java_document:
            return Document.python_document_from_java(java_document)
        else:
            return None

    def _find_by_java_document_stream(self, document_stream):
        iterator = document_stream.iterator()

        while iterator.hasNext():
            yield Document(java_to_python_cast(iterator.next()))
        document_stream.close()

    @handle_java_exceptions
    def find(self, columns=None):
        """
        Returns a generator that iterates over all documents in the table, possibly returning only some columns.

        :param columns: list of strings, which
        specifies certain columns to select from the returned document.
        :returns: generator, which returns maprdb.document.Document class instances.
        """
        document_stream = self.java_table.find(columns) if columns else self.java_table.find()
        return self._find_by_java_document_stream(document_stream)


    def find_by_condition(self, condition, columns=None):
        """
        Returns a generator that iterates over all documents that satisfy the passed condition.

        :param condition: maprdb.document.Condition class instance
        :param columns: list of strings, which
        specifies certain columns to select from the returned document.
        :returns: generator, which returns maprdb.document.Document class instances.
        """
        document_stream = self.java_table.find(python_to_java_cast(condition), columns) if columns else self.java_table.find(python_to_java_cast(condition))
        return self._find_by_java_document_stream(document_stream)

    def _fill_document_key(self, doc, key=None):
        if '_id' not in doc:
            if key is None:
                raise MapRDBError("No key or _id property in document is specified.")
            doc = copy.copy(doc)
            doc['_id'] = key
        else:
            if not key is None:
                raise MapRDBError("Both key and _id property in document are specified.")
        return doc

    @handle_java_exceptions
    def insert(self, doc, key=None):
        """
        Insert the document in the database. If the document already exists,
        maprdb.utils.MapRDBError is raised

        :param doc: maprdb.document.Document class instance, that should have an _id field. If not present an exception should be raised.
        If the user specific a key, it will be added to the document automatically as _id field, if the document contains an _id and a key is passed, an maprdb.utils.MapRDBError will be raised.
        Finally if a document with this key already exist maprdb.utils.MapRDBError will be raised by the server as well.
        :param key: string value, which is _id of the record to find.
        """
        doc = self._fill_document_key(doc, key=key)
        self.java_table.insert(python_to_java_cast(doc))

    @handle_java_exceptions
    def insert_or_replace(self, doc, key=None):
        """
        Insert the document in the database. If the document already exists, it gets replaced.

        :param doc: maprdb.document.Document class instance, that should have an _id field. If not present an exception should be raised.
        If the user specific a key, it will be added to the document automatically as _id field, if the document contains an _id and a key is passed, an maprdb.utils.MapRDBError will be raised.
        :param key: string value, which is _id of the record to find.
        """
        doc = self._fill_document_key(doc, key=key)
        self.java_table.insertOrReplace(python_to_java_cast(doc))

    @handle_java_exceptions
    def update(self, key, mutation):
        """
        Performs the requested mutation on the document with the specified key(s).

        :param key: string value or list of strings, if it is a list,
        then the same mutation will be applied to each document specified by the elements of the list.
        :param mutation: maprdb.mutation.Mutation class instance, which is a mutation to perform.
        """
        keys_list = key if isinstance(key, (list,tuple)) else [key]

        for k in keys_list:
            self.java_table.update(k, python_to_java_cast(mutation))

    @handle_java_exceptions
    def update_all(self, values):
        """
        For every dictionary entry, performs the requested mutation on the document with the specified key(s).

        :param values: dict value, which as key has a key of document to update, and as a value has a mutation,
        to perform on it.
        """
        for k in values.keys():
            self.update(k, values[k])

    @handle_java_exceptions
    def delete(self, key):
        """
        Deletes the document with the specified key.

        :param key: string value or list of strings, ff it is a list, documents matching the keys are deleted as a batch.
        """
        keys_list = key if isinstance(key, (list,tuple)) else [key]

        for k in keys_list:
            self.java_table.delete(k)

    @handle_java_exceptions
    def flush(self):
        """
        Forces all pending operations to be performed. Returns on completion.
        Operations may be flushed by the library before the flush is requested.
        """
        self.java_table.flush()

    @handle_java_exceptions
    def close(self):
        """
        Close table. This method should always be called after using the table.
        """
        self.java_table.close()
