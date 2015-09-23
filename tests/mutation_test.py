import unittest
import logging
from maprdb import Mutation
from tests.base import BaseMapRDBTest


class TestConnection(BaseMapRDBTest):
    def test_append(self):
        mutation = Mutation().set("sfasfa",[542.3,12.3,4.4,12.5])\
        .set("address.line", "{'a':2,'b':3}")\
        .set("something", 3.45)\
        .set("address.zip", 94065)\
        .append("something.to.append", "qwerty")\
        .append("something.to.append.list", [542.3,12.3,4.4,12.5])\
        .increment("something.to.increment", 21)\
        .decrement("something.to.decrement", 1)\
        .delete("field_deleted")\
        .build()
        self.assertTrue(isinstance(mutation, Mutation), "Mutation instance should be returned!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
