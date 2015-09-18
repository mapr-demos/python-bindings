import unittest
import logging
import maprdb
import datetime
from maprdb.conditions import Condition
from maprdb.utils import MapRDBError
from maprdb.document import Document
from tests.base import BaseMapRDBTest
from maprdb.mutation import Mutation

class TestMapRDBConnection(BaseMapRDBTest):
    def test_no_two_jvm(self):
        self.assertRaises(Exception, maprdb.connect)

    def test_create_table(self):
        if self.connection.exists("/tmp/test_table"):
            self.connection.delete("/tmp/test_table")

        self.assertFalse(self.connection.exists("/tmp/test_table"))
        table1 = self.connection.create("/tmp/test_table")
        self.assertTrue(self.connection.exists("/tmp/test_table"))

        # add datetime datetime
        document1_key = "test_table_1"
        document1 = Document({'_id': document1_key, 'count': 7})
        table1.insert_or_replace(document1)
        
        mutation1 = Mutation().increment('count', 5)
        
        table1.update(document1_key, mutation1)
        table1.flush()
        
        self.assertEqual(table1.find_by_id(document1_key), document1)
        
        document2 = Document({'some_number': 33, 
                          'some_float': 3.1,
                          'some_string': 'str',
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
        
        all_table_docs = [x for x in table1.find()]
        self.assertEqual(len(all_table_docs), 1)
        
        document2.update({'_id': document1_key})
        self.assertEqual(document2, all_table_docs[0])
        self.assertEqual(document2, table1.find_by_id(document1_key))
        
        mutation1 = Mutation().increment("some_number", 4).\
        append("some_list", [1,2,3]).\
        delete("some_string").\
        decrement("some_float", 1.0).\
        build()      

        table1.update(document2_key, mutation1)
        table1.flush()
        
        expected_document = {'some_number': 37, 
                             'some_float': 2.1, 
                             'some_date': datetime.datetime(2015, 9, 10, 12, 27, 35), 
                             'some_list': [5, 6, 7, 1, 2, 3], 
                             '_id': document2_key, 
                             'some_dict': {'b': 6.25, 'a': 7}
        }
        self.assertEqual(table1.find_by_id(document2_key), expected_document)

        document3 = Document({'some_number': 1, 
                          'some_float': 55.1,
                          'some_string': 'newstr',
                          'some_date': datetime.datetime(2019, 9, 10, 12, 21, 35),
                          'some_list': ['a', 'b', 'c'],
                          'some_dict': {'zyx': 1, 'abc':64.25}
        })
        document3_key = "test_table_2"
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
        expected_result1 = [{'some_float': 1.1, 'some_date': datetime.datetime(2015, 9, 10, 12, 27, 35)}, {'some_float': 60.1, 'some_date': datetime.datetime(2019, 9, 10, 12, 21, 35)}]
        result1 = [x for x in table1.find_by_condition(condition1, columns=['some_date', 'some_float'])]
        self.assertEqual(result1, expected_result1)
        
        condition2 = Condition([{ "some_date": datetime.datetime(2019, 9, 10, 12, 21, 35)}, {"some_float": {"$gt": 30}}])
        expected_result2 = [{'some_float': 60.1}]
        result2 = [x for x in table1.find_by_condition(condition2, columns=['some_float'])]
        self.assertEqual(result2, expected_result2)

        self.assertEqual(len([x for x in table1.find()]), 2)
        table1.delete(document2_key)
        table1.flush()
        self.assertEqual(len([x for x in table1.find()]), 1)
        table1.delete(document3_key)
        table1.flush()
        self.assertEqual(len([x for x in table1.find()]), 0)
        
        table1.delete(document1_key)
        self.connection.delete("/tmp/test_table")
        self.assertFalse(self.connection.exists("/tmp/test_table"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
