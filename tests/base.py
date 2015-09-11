import unittest
import logging
import jpype
from tests.utils import maprdb_connect


class BaseMapRDBTest(unittest.TestCase):

    def setUp(self):
        try:
            self.connection = maprdb_connect()
        except:
            self.fail("connection() raised unexpected exception")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
