from maprdb.utils import python_to_java_cast, java_to_python_cast


class Document(dict):
    def __init__(self, d, *args, **kwargs):
        dict_retained = d
        super().__init__(dict_retained, *args, **kwargs)

    @staticmethod
    def python_document_from_java(java_object):
        return Document(java_to_python_cast(java_object))

    def _get_java_object(self):
        from maprdb.connection import Connection
        maprdb = Connection.get_instance().MapRDB
        java_document = maprdb.newDocument()

        for k,v in self.items():
            java_document.set(python_to_java_cast(k),python_to_java_cast(v))

        return java_document
