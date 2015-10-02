import time, sys
import unittest
import logging
import maprdb
import datetime
from maprdb.conditions import Condition
from maprdb.utils import MapRDBError
from maprdb.document import Document
from tests.base import BaseMapRDBTest
from maprdb.mutation import Mutation
import maprdb.connection


class TestMapRDBConnection(BaseMapRDBTest):
    def test_no_two_jvm(self):
        with self.assertLogs(level=logging.WARN):
            maprdb.connect()  # not raises exception, but warning about inability to start second JVM

    def test_create_table(self):
        if self.connection.exists("/tmp/test_table"):
            self.connection.delete("/tmp/test_table")
        self.assertFalse(self.connection.exists("/tmp/test_table"))

        self.connection.create("/tmp/test_table")
        self.assertTrue(self.connection.exists("/tmp/test_table"))

    def test_integration(self):
        """
        Comprehensive test which includes most of features
        """
        if self.connection.exists("/tmp/test_table2"):
            self.connection.delete("/tmp/test_table2")
        table1 = self.connection.create("/tmp/test_table2")

        # add datetime datetime
        document1_key = "doc1"
        document1 = Document({'_id': document1_key, 'count': 7})
        table1.insert_or_replace(document1)
        table1.flush()

        mutation1 = Mutation().increment('count', 5)
        table1.update(document1_key, mutation1)
        table1.flush()

        self.assertEqual(table1.find_by_id(document1_key)['count'], 12)

        document2 = Document({'some_number': 33,
                          'some_float': 3.1,
                          'some_string': 'str',
                          'some_string2': 'abc',
                          'some_date': datetime.datetime(2015, 9, 10, 12, 27, 35),
                          'some_list': [5,6,7],
                          'some_dict': {'a': 7, 'b':6.25}
        })
        document2_key = document1_key # replace

        # insert using existing key should raise error
        with self.assertRaises(MapRDBError):
            table1.insert(document2, key=document2_key)

        table1.insert_or_replace(document2, key=document2_key)
        table1.flush()

        table_docs_shorted = [x for x in table1.find(columns=['some_float', 'some_string'])]
        self.assertEqual(len(table_docs_shorted), 1)
        self.assertEqual(table_docs_shorted[0], {'_id': 'doc1', 'some_string': 'str', 'some_float': 3.1})

        all_table_docs = [x for x in table1.find()]
        self.assertEqual(len(all_table_docs), 1)

        document2.update({'_id': document1_key})
        self.assertEqual(document2, all_table_docs[0])
        self.assertEqual(document2, table1.find_by_id(document1_key))


        mutation0 = Mutation().increment("some_number", 4).\
        append("some_list", [1,2,3]).\
        append("some_string2", "def").\
        delete("some_string").\
        decrement("some_float", 1.0).\
        set("some_new_field", 123).\
        build()

        mutation1 = Mutation([
          {"some_number": {"$inc": 4}},
          {"some_list": {"$append": [1,2,3]}},
          {"some_string2": {"$append": "def"}},
          {"some_string": {"$delete": []}},
          {"some_float": {"$dec": 1.0}},
          {"some_new_field": {"$set": 123}},
        ]).build()

        self.assertEqual(mutation0.java_mutation.record, mutation1.java_mutation.record)

        table1.update(document2_key, mutation1)
        table1.flush()


        expected_document = {'some_number': 37,
                             'some_string2': 'abcdef',
                             'some_float': 2.1,
                             'some_date': datetime.datetime(2015, 9, 10, 12, 27, 35),
                             'some_list': [5, 6, 7, 1, 2, 3],
                             '_id': document2_key,
                             'some_dict': {'b': 6.25, 'a': 7},
                             'some_new_field': 123
        }
        self.assertEqual(table1.find_by_id(document2_key), expected_document)

        document3 = Document({'some_number': 1,
                          'some_float': 55.1,
                          'some_string': 'newstr',
                          'some_date': datetime.datetime(2019, 9, 10, 12, 21, 35),
                          'some_list': ['a', 'b', 'c'],
                          'some_dict': {'zyx': 1, 'abc':64.25}
        })
        document3_key = "doc3"
        table1.insert(document3, key=document3_key)
        table1.flush()

        mutation2 = Mutation().decrement('some_float', 1).build()
        mutation3 = Mutation().increment('some_float', 5).build()

        table1.update_all({
          document2_key: mutation2,
          document3_key: mutation3,
        })
        table1.flush()

        self.assertEqual(table1.find_by_id(document2_key)['some_float'], 1.1)
        self.assertEqual(table1.find_by_id(document3_key)['some_float'], 60.1)

        condition1 = Condition([{ "some_date": datetime.datetime(2019, 9, 10, 12, 21, 35)}, {"some_float": {"$gt": 0}}])
        expected_result1 = [{'some_date': datetime.datetime(2015, 9, 10, 12, 27, 35), '_id': document2_key, 'some_number': 37}, {'some_date': datetime.datetime(2019, 9, 10, 12, 21, 35), '_id': document3_key, 'some_number': 1}]
        result1 = [x for x in table1.find_by_condition(condition1, columns=['some_date', 'some_number'])]
        self.assertEqual(result1, expected_result1)

        condition2 = Condition([{ "some_date": datetime.datetime(2019, 9, 10, 12, 21, 35)}, {"some_float": {"$gt": 30}}])
        expected_result2 = [{'_id': document3_key, 'some_number': 1}]
        result2 = [x for x in table1.find_by_condition(condition2, columns=['some_number'])]
        self.assertEqual(result2, expected_result2)

        self.assertEqual(len([x for x in table1.find()]), 2)
        table1.delete([document2_key,document3_key])
        table1.flush()
        self.assertEqual(len([x for x in table1.find()]), 0)

        self.assertIsNone(table1.find_by_id("non_existing_document"))

        table1.delete(document1_key)
        self.connection.delete("/tmp/test_table2")
        self.assertFalse(self.connection.exists("/tmp/test_table2"))

        table1.close()

    def test_typeerror_raise(self):
        with self.assertRaises(TypeError):
            self.connection.exists(42)  # parameter should be string


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
