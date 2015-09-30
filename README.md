# python-bindings
Python bindings for MapR DB JSON API

## How to Build
Requirements:

  - Python 3
  - Maven - `mvn` command should be in PATH.
  - GCC and python headers could be required to build dependencies

To install this package run

    python setup.py install

## Running unit tests

  - Add /etc/hosts entry like `172.16.42.129	maprdemo` that points to the instance with MapRDB running
  - Run unit tests
```
pip install pytest
py.test
```

## Note
The empty dependencies directory is used at build time. Maven will
download all necessary dependent jars and put them in this directory.

Then at run-time, the class path will be set so as to include all
the jars in this directory.

Due to limitation of Java interfacing library, only one JVM can be started during Python interpreter session. Since connection parameters to MapRDB should be specified
in JVM parameters, hence only one connection to MapRDB can be opened. First call of maprdb.connect() starts JVM, all
subsequent calls will return same connection with warning message.

## Example

```
from maprdb import connect, Document, Mutation
# Make connection to MapRDB
connection = connect("/path/to/mapr/config")  # argument is not required

# Create some document
document1_key = "doc1"
document1 = Document({'_id': document1_key, 'count': 7})

# Delete table if it's already present. Note JVM will be created only here,
# on the first place it is required
if connection.exists("/tmp/test_table"):
    connection.delete("/tmp/test_table")
table1 = connection.create("/tmp/test_table")

# Adding previously created document to the table
table1.insert_or_replace(document1)

# Making Mutation object and applying it to the document
mutation1 = Mutation().increment('count', 5)
table1.update(document1_key, mutation1)

table1.flush()

# Reading the document doc1
print(table1.find_by_id(document1_key))
>>> {'_id': 'doc1', 'count': 12}
```

## Troubleshooting

  - Exception `MapRDBError: com.mapr.db.exceptions.DBException: method() failed.` 
and log line `ERROR Client fs/client/fileclient/cc/client.cc:864 Thread: 4187 Failed to
initialize client for cluster demo.mapr.com, error Connection reset by peer(104)` - it means that host with MapRDB
you're trying to connect to is not accessible, check your connect() call and `mapr-clusters.conf` file.

  - `maprdb.connect()` returns connection with warning "Only one connection can be opened, previously created connection
will be used." - that happened because you called connect() several times. Only one connection can be opened during one Python
interpreter session, so `connect()` always returns very first opened connection. See Note for details.
