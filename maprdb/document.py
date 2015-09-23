from maprdb.utils import python_to_java_cast, java_to_python_cast


class Document(dict):
    def __init__(self, d, *args, columns_to_retain=None, **kwargs):
        if columns_to_retain:
            dict_retained = {k:v for (k,v) in d.items() if k in columns_to_retain}
        else:
            dict_retained = d
            
        super().__init__(dict_retained, *args, **kwargs)

    @staticmethod
    def python_document_from_java(java_object, columns_to_retain=None):
        return Document(java_to_python_cast(java_object), columns_to_retain=columns_to_retain)

    def _get_java_object(self):
        from maprdb.connection import Connection
        maprdb = Connection.get_instance().MapRDB
        java_document = maprdb.newDocument()

        for k,v in self.items():
            java_document.set(python_to_java_cast(k),python_to_java_cast(v))

        return java_document
