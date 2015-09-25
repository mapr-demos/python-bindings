from collections import OrderedDict
import datetime
import unittest
import logging
from maprdb import Condition
from maprdb.conditions import Op
from tests.base import BaseMapRDBTest


class TestFluentConditions(BaseMapRDBTest):
    """
    Test fluent interface. It's not supposed to be open, but it's base
    interface for shorthand input.
    """
    def test_date(self):
        c = Condition(). \
            _and(). \
            _is("dob", Op.GREATER_OR_EQUAL, datetime.date(year=1980, month=1, day=1)). \
            _is("dob", Op.LESS, datetime.date(year=1981, month=1, day=1)). \
            _close()
        self.assertEqual(c.java_condition.toString(),
                         '((dob >= {"$dateDay":"1980-01-31"}) and (dob < {"$dateDay":"1981-01-31"}))')

    def test_time(self):
        now = datetime.datetime.now().time()
        utc_now = datetime.datetime.utcnow().time()  # maprdb converts to UTC
        c = Condition(). \
            _is("t", Op.EQUAL, now)
        self.assertEqual(c.java_condition.toString(), '(t = {"$time":"%s"})' % utc_now.strftime("%H:%M:%S"))

    def test_timestamp(self):
        now = datetime.datetime.now().replace(microsecond=0)
        utc_now = datetime.datetime.utcnow().replace(microsecond=0)  # maprdb converts to UTC
        c = Condition(). \
            _is("t", Op.EQUAL, now)
        self.assertEqual(c.java_condition.toString(), '(t = {"$date":"%s.000Z"})' % utc_now.isoformat())


class TestShorthandConditions(BaseMapRDBTest):
    def test_and(self):
        c = Condition(OrderedDict([("country", "China"), ("age", 34)]))
        self.assertEqual(c.java_condition.toString(), '((country = "China") and (age = {"$numberLong":34}))')

    def test_or(self):
        c = Condition([{ "country": "China"}, {"age": 34}])
        self.assertEqual(c.java_condition.toString(), '((country = "China") or (age = {"$numberLong":34}))')

    def test_eq_alias(self):
        c = Condition({ "country": "China"})
        self.assertEqual(c.java_condition.toString(), '(country = "China")')

    def test_operator_eq(self):
        c = Condition({"country": {"$eq": "China"}})
        self.assertEqual(c.java_condition.toString(), '(country = "China")')

    def test_operator_ne(self):
        c = Condition({"country": {"$ne": "China"}})
        self.assertEqual(c.java_condition.toString(), '(country != "China")')

    def test_lt(self):
        c = Condition({"age": {"$lt": 34}})
        self.assertEqual(c.java_condition.toString(), '(age < {"$numberLong":34})')

    def test_le(self):
        c = Condition({"age": {"$le": 34}})
        self.assertEqual(c.java_condition.toString(), '(age <= {"$numberLong":34})')

    def test_gt(self):
        c = Condition({"age": {"$gt": 34}})
        self.assertEqual(c.java_condition.toString(), '(age > {"$numberLong":34})')

    def test_ge(self):
        c = Condition({"age": {"$ge": 34}})
        self.assertEqual(c.java_condition.toString(), '(age >= {"$numberLong":34})')

    def test_between(self):
        c = Condition({"age": {"$between": [12, 34]}})
        self.assertEqual(c.java_condition.toString(), '((age >= {"$numberLong":12}) and (age <= {"$numberLong":34}))')

    def test_in(self):
        c = Condition({"age": {"$in": [1, 2]}})
        self.assertEqual(c.java_condition.toString(), '((age = {"$numberLong":1}) or (age = {"$numberLong":2}))')

    def test_not_in(self):
        c = Condition({"age": {"!$in": [1, 2]}})
        self.assertEqual(c.java_condition.toString(), '((age != {"$numberLong":1}) and (age != {"$numberLong":2}))')

    def test_exists(self):
        c = Condition({"age": {"$exists": True}})
        self.assertEqual(c.java_condition.toString(), '(age != null)')

        c = Condition({"age": {"$exists": False}})
        self.assertEqual(c.java_condition.toString(), '(age = null)')

    def test_like(self):
        c = Condition({"age": {"$like": "1024 V.*"}})
        with self.assertRaises(NotImplementedError):
            c._get_java_object()

    def test_not_like(self):
        c = Condition({"age": {"!$like": "1024 V.*"}})
        with self.assertRaises(NotImplementedError):
            c._get_java_object()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
