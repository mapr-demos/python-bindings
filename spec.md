# Python Bindings for MapR DB JSON API

## Package maprdb


`maprdb = mapr.connection(“cldb info”)` Opens a connection to a MapR server.


`maprdb.delete(“name”)` Deletes a table


`table = maprdb.create(“name”)` Creates a table and returns a reference of type maprdb.Table


`table = maprdb.get(“name”)` Finds a table and returns a reference of type maprdb.Table


`maprdb.exists(“name”)` Returns a boolean value according to whether the table exists.


`maprdb.setOptions(map)` Sets the options specified in the map. No options are currently defined, but it is expected that there may be options such as audit and autoflush.
`map = maprdb.getOptions()` Returns the current values of all options
in a map.

## maprdb.Table operations

`t.findById(key, columns=None)` Returns the specified fields of the
document with the specified key. If the columns parameter is not
provided, the default is to return all columns of the document.

If key is a list, return a list of results, one for each key value.
Results (documents) are returned as a dict where the keys are the keys
of the documents and the values are the documents themselves.

`t.find(columns=None)` Returns a generator that iterates over all
documents, possibly returning only some columns. If the columns
argument is omitted, all fields are returned.


`t.find(condition, columns=None)` Returns a generator that iterates
over all documents that satisfy the condition. Note that the condition
should be a Condition object or a value that can be used to construct
a Condition. If the columns parameter is supplied, only those fields
will be returned. If not supplied, all fields will be returned.

Example:
```python
chinese_users = t.find({‘country’:'China'})
```
OR:
```python
chinese_users_stats = t.find({‘country’:'China'}, [“city”, “age”, “prefs”])
```

`t.insert(document, key=None)` Insert the document (see Document spec
below) in the database.  If the key not specified, the document should
have an `_id` field.  If the user specifies a key, it will be added to
the document automatically, if the document contains an _id and a key
is passed, an error will be raised.  Finally, if a document with this
key already exist an exception will be raised by the server. All
exceptions other than those due to invalid arguments may be raised
when a `flush()` or `close()` is called on the underlying exception
due to write-caching.


`t.insert_all(values)` Creates a document for each key value pair in
values as a batch. Throws exception on error. This is a
client side non-atomic insert of the list of document. All
exceptions other than those due to invalid arguments may be raised
when a `flush()` or `close()` is called on the underlying exception
due to write-caching.


`t.insert_or_replace(document, key=None)` This method is the same as
the `insert()` method, except that if a document with the key/_id
already exists, this document will simply be replaced.


A future extension may support inserting or replacing many documents
in a single operation analogously to update_all and insert_all. The
specification of this operation will be:
`t.insert_or_replace_all(values)` For each key in values (a dict-like object), the key and value will be sent to insert_or_replace(). This is not atomic and it would be desirable to implement this server-side when possible. The semantics should be equivalent to this:

```python
   for k in values.keys():
        t.insert_or_replace_all(key, values[key])
```	
`t.update(key, mutation)` Performs the requested mutation on the document with the specified key. Throws an exception on error. Any exceptions will be thrown when flush is called.  If key is a list, then the same mutation will be applied to each document specified by the elements of the list.

A future extension may allow mutations to be applied based on a
condition. This extension will include this method:

`t.update_conditionally(condition, mutation)` Performs the requested
mutation on all documents that match the specified condition.
	
`t.update_all(values)` The values are assumed to be in a dict-like object. this should be equivalent to

```python
    for k in values.keys():
        t.update(key, values[key])
```

Note that updates done this way are not done in a transaction. In the
initial implementation, we may need to emulate this functionality on
the client side.

`t.delete(key)` Deletes the document with the specified key. If key is a list, documents matching the keys are deleted as a batch. Throws exception if document not found. Throws exception on error. Any exceptions will be thrown when flush is called


`t.flush()` Forces all pending operations to be performed. Returns on completion. Operations may be flushed by the library before the flush is requested. All errors from operations executed before the flush may actually be raised by the flush instead of the original operation. Note that close or flush must be called to ensure that all operations are performed.

## maprdb.Document

Documents returned from the database will be returned as a Document
object which is a dict-style object with fields that can be addressed
using string names. That is:

```python
    doc = t.find(“foo-document”)
    x = [doc[i] for i in [“first_name”, “last_name”]]
```

## maprdb.Mutation operations

`m = Mutation()` A mutation is a specification of changes to be made
to a document.

`m.set(“field”, value)` Set the specified field to the specified value which can be scalar, a list or a dict.

`m.append(“field”, value)` Append the specified field to the specified value which can be scalar, a list or a dict.


`m.increment(field, value=1)` Increment the value of a field. The
field should already contain a numeric value. The operation will fail
and raise an exception if the increment is applied to a field
containing a non-numeric value. 

`m.decrement(field, value=1)` Decrement the value of a field. The
field should already contain a numeric value. The operation will fail
and raise an exception if the decrement is applied to a field
containing a non-numeric value.

`m.delete(field)` Deletes a field in a document

Mutations should also support being constructed using the
micro-language supported by the JS API. In this micro-language, a
mutation can be specified using a dict where the fields to be mutated
are the keys and the values are objects which describe what is to be
changed. The values can be scalars (which is a short-hand for a
$setOrReplace operation) or objects. Setting a field unconditionally
to a scalar value can be done using a short-cut

```javascript
{"field": 3}   // set or replace age to 34
```

But most updates require a more elaborate syntax

```json
{"field" : { "$set" : "value"}  }
{ "field" : { "$append" : "value" }}
{"age" : { "$inc" : 1 } } //  increment one value by a specified amount
```

See the wiki page on the [mutation micro language](https://github.com/mapr-demos/js-bindings/wiki/Mutation-micro-language)
for more details.

## maprdb.Condition operations

A condition is a specification of which documents are desired in a
query. A condition can exist independently of any document or table
and is merely used to specify a filter that describes which documents
are desired. Conditions can be constructed using a fluent API or 
```python
c = Condition()
c.and()
c.or()
c.close()
c.exists(“field”)
c.notExists(“field”)
c.is(field, condition, value)
c.build()
```

These methods have to appear according to the following grammar:

condition ::= { 
    /* empty */ | <op> <condition> close() | is(field, condition, value)
    }
    build()
op ::= and() | or()

If methods are called out of order, an exception should be raised.

As a short-cut, a condition can be constructed by supplying a dict or
list to the constructor.

`c = Condition(map)` Builds a condition that constrains the values of
the fields in documents. The keys of the dict specify the fields whose
values are to be limited and the values of the dict specify the
constraint.

`c = Condition(list)` Builds a condition that is the disjunction (OR
combination) of the conditions in the list.

Both of these constructors are simply short-hand for the fluent API.

Example:
```python
    c = Condition({“country”:”us”})
     c = Condition({
           “amount”:{“<”:1000}}, 
           “address”, {“$matches”:”1024 V.*”}})
```
## Sample conditions

Conditions are created fairly conventionally and have several forms of
short-cuts to handle very common cases. In general, a condition looks
like a mirror of some of the fields in the document except that values
are replaced by comparison functions. The most common short-cut is
that scalar values are short-cuts for an equality test with those
values.

For example, equality with a scalar value can have a short-cut expression:

```json
{ "country" : "China" } // country == "China"
```

Test for structured values like this:

```json
{ "country" : {"$eq": ["China","United States"]} } 
```

Many other tests are also available.  See
the wiki page on [the condition micro language](https://github.com/mapr-demos/js-bindings/wiki/Condition-Micro-Language)
for more details.


# Required
1. Idiomatic Python interface
2. Native maps and lists should translate into appropriate API concepts
3. Must support generator/iterator style for
   1. range queries
   2. restriction to columns
   3. key and column filtering
1. Requirement (2) must work for common flow control including
   1. list and set comprehensions
   2. iterations
1. The most most straightforward way to implement this API may be through the use of a Java/Python gateway module, such as is described in the next section.


### Using a JNI Gateway to call Python from Java


The Java Native Interface (JNI) is a mechanism that allows application code to call Java code running in a JVM instance.  There are several freely available packages, with various open-source licenses, that implement this functionality for common languages such as Python and C++.  Some of the architectures require maintaining an external server ‘gateway’, by hand, that runs as a separate process. An external gateway is not an acceptable solution.


One such package that seems to work with the MapR-DB JSON API is pyjnius, which is one of the simplest to use and does not require starting/stopping a gateway manually in the code.  The following installation steps are required. 


1. Follow the pyjnius installation steps according to the author’s instructions.  This example works well on Linux Ubuntu 14.04, instructions on a Mac or other machine may be different.


1. To test an example with MapR-DB, clone the Argonaut 101 example into a local repo.


1. Test the setup with the following steps:


   1. In the base directory of the Argonaut 101 example above, pull all of the dependency jars into a local filesystem (there may be a better way to do this, and/or it may not be required, but that’s untested).


      1. mvn dependency:copy-dependencies (this copies the dependencies into the target/dependency directory)


      1. In the target/dependency directory, unzip all of the newly downloaded .jar files (again this may not be required but seemed to be necessary in the test setup).


      1. Ensure that the cwd (“.”) is in the classpath.


   1. Create the table in the MCS or with the MapR CLI commands.  The table creation API did not appear to work yet in a first pass.


   1. You can now instantiate the Java classes and call their methods from Python.  Here’s an example script to add entries into a table, reading from a JSON file.

```python
#!/usr/bin/python
from jnius import autoclass
import json


mdb = autoclass('com.mapr.db.MapRDB')
p = "/tmp/wellsensors"
t = mdb.getTable(p)
with open('/tmp/new.json') as json_data:
        d = json.load(json_data)
        for doc in d:
                thisdoc = mdb.newDocument()
                thisdoc.set("hcid", str(doc["hcid"]))
                thisdoc.set("timestamp", str(doc["timestamp"]))
                thisdoc.set("production", str(doc["production"]))
                t.insertOrReplace(str(doc["event_id"]), thisdoc)
```	

The following code queries the table we just loaded.


```python
#!/usr/bin/python
from jnius import autoclass

r = t.findById("99")
st = r.getBinary("timestamp")
jstr = autoclass('java.lang.String')
pyjstr = jstr(st.array()).toString()
print str(pyjstr)
```	

Note that a few awkward transformations may be required to routinely access the data (i.e. instantiating a String, converting the MapR-DB byte buffer to an array, then to a String).  The API should hide this from the user.  Ideally there should be some mappings to common native types in Python.
