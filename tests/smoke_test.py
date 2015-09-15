import unittest
import logging
import jpype
from tests.base import BaseMapRDBTest


class TestJPypeJVM(BaseMapRDBTest):
    """
    Test if JPype can start JVM and do basic operations
    """
    def test_append(self):
        string = jpype.JClass("java.lang.String")
        hello_str = string("Hello, ").concat("World")
        self.assertEqual(str(hello_str), "Hello, World")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
