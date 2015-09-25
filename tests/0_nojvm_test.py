"""
unittest sorts all tests alphabetically, so name of file
starts from '0' intentionally to make this case run before all others.
"""

import unittest
import logging
import jpype
from maprdb import Condition, Document


class TestNoJVM(unittest.TestCase):
    """
    Tests which should be executed when JVM is not yet started.
    """
    def setUp(self):
        if jpype.isJVMStarted():
            self.fail("JVM should not be started to run this TestCase")

    def test_condition_no_jvm(self):
        Condition({"country": {"$ne": "China"}})

    def test_document_no_jvm(self):
        Document({"name": "Peter"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
