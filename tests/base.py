import unittest
import logging
from tests.utils import maprdb_connect


class BaseMapRDBTest(unittest.TestCase):
    """
    Base test class, opens connection to MapRDB.
    """
    def setUp(self):
        try:
            self.connection = maprdb_connect()
        except:
            self.fail("connection() raised unexpected exception")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
