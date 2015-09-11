import unittest
import logging
import maprdb
from tests.base import BaseMapRDBTest


class TestMapRDBConnection(BaseMapRDBTest):
    def test_no_two_jvm(self):
        self.assertRaises(Exception, maprdb.connect)

    def test_create_table(self):
        if self.connection.exists("/tmp/test_table"):
            self.connection.delete("/tmp/test_table")
        self.assertFalse(self.connection.exists("/tmp/test_table"))
        self.connection.create("/tmp/test_table")
        self.assertTrue(self.connection.exists("/tmp/test_table"))
        self.connection.delete("/tmp/test_table")
        self.assertFalse(self.connection.exists("/tmp/test_table"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
