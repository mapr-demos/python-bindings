Please consider using the [maprdb-python-client](https://pypi.org/project/maprdb-python-client/#description) package instead.

See MapR documentation:
https://mapr.com/docs/home/MapR-DB/JSON_DB/GettingStartedPythonOJAI.html

# python-bindings
This repo hosts a Python module that implements lightweight bindings for
the MapR-DB JSON API, also known as the Open JSON Application Interface
(OJAI).

## Requirements

  - Python 3
  - Maven - the `mvn` command should be in the $PATH.
  - GCC (for C and C++) and Python headers may be required to build dependencies
  - The `mapr-client` must be installed and configured, or run the module directly on MapR node.

## Quickstart

You can install the package from the source in this repo or via pip.
The installation process will pull the .jar files necessary to interact
with your MapR-DB installation to provide the underlying support for
the Python API.

An installation via either method may take several minutes because of the need to download these dependencies.

### Installing via source

To install via source the following additional requirements must be met:

* `setuptools` must be installed (installable via `pip3` or `pip`)
* Python 3 headers are recommended:  this is usually installable via
  the pythonXX-devel package for your system

Check out the repo:

    # git clone https://github.com/mapr-demos/python-bindings
    # cd python-bindings

Edit the `pom.xml` file to match the version of the MapR platform you
are using.  This is under the dependency for `com.mapr.db`:

    <dependencies>
      <dependency>
        <groupId>com.mapr.db</groupId>
        <artifactId>maprdb</artifactId>
        <version>5.2.1-mapr</version>
      </dependency>
    </dependencies>

Install the package:

    # python3 setup.py install

###  Installing via `pip`

In many installations `pip3` is the command to install a Python 3 package.

    # pip3 install maprdb
    (...)
    Collecting maprdb
    Collecting JPype1==0.6.1 (from maprdb)
    Collecting multipledispatch (from maprdb)
      Downloading multipledispatch-0.4.8.tar.gz
    Building wheels for collected packages: maprdb, JPype1, multipledispatch
      Running setup.py bdist_wheel for maprdb
      Running setup.py bdist_wheel for JPype1
      Running setup.py bdist_wheel for multipledispatch
    Successfully built maprdb JPype1 multipledispatch
    Installing collected packages: JPype1, multipledispatch, maprdb
    Successfully installed JPype1-0.6.1 maprdb-0.0.2 multipledispatch-0.4.8

## Running unit tests

The included unit tests can be run if you have one or more nodes of MapR
available.  The unit tests assume a host named `maprdemo` is running
MapR-DB and available.  You can add an entry to `/etc/hosts` such as
`172.16.42.129 maprdemo` that points to the instance with MapRDB running.

To run the unit tests:

Ensure that `pytest` is installed:

`pip3 install pytest`

Then,

`python3 py.test`

## Additional Notes

The empty dependencies directory is used at build time. Maven will
download all necessary dependent jars and put them in this directory.

Then at run-time, the class path will be set so as to include all
the jars in this directory.

Due to a limitation in the Java interfacing library, only one JVM can be
started during Python interpreter session. Connection parameters to
MapRDB should be specified in JVM parameters, hence only one connection
to MapRDB can be opened.

The first call of maprdb.connect() starts the JVM.  All subsequent calls
will return the same connection with a warning message.

## Example Usage

Also see
[this demo repo](https://github.com/mapr-demos/maprdb_python_examples)
for a full example.
    
    from maprdb import connect, Document, Mutation
    # Make connection to MapRDB
    connection = connect("/path/to/mapr/config")  # argument is not required
    
    # Create some document
    document1_key = "doc1"
    document1 = Document({': document1_key, 'count': 7})
    
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

## Troubleshooting

Common configuration issues/errors are found here.

#### Cannot connect to the cluster
```
Exception `MapRDBError: com.mapr.db.exceptions.DBException: method()
failed.` along with a line in the log:
`ERROR Client fs/client/fileclient/cc/client.cc:864
Thread: 4187 Failed to initialize client for cluster demo.mapr.com,
error Connection reset by peer(104)`
```

The MapR-DB host(s) are not accessible.  Check your `mapr-clusters.conf` file
or review the documentation for client-side configurations [here](http://maprdocs.mapr.com/home/AdvancedInstallation/SettingUptheClient-mapr-client.html).
this means that host with MapRDB
you're trying to connect to is not accessible, check your connect()
call and `mapr-clusters.conf` file.

#### Calling connect() multiple times in your code

`maprdb.connect()` returns connection with warning `"Only one
 connection can be opened, previously created connection
will be used."`

This happens because your code called connect() several
times. Only one connection can be opened during one Python interpreter
session, so `connect()` always returns very first opened connection.
See the above section under Additional Notes for details.

#### Java .jars version mismatch with native version
```
ERROR JniCommon fs/client/fileclient/cc/jni_MapRClient.cc:684
Thread: 47421 Mismatch found for java and native libraries java build
version 5.2.1.42646.GA, native build version 6.0.0.44429.BETA java
patch vserion $Id: mapr-version: 5.2.1.42646.GA 42646:812878ab1269
$, native patch version $Id: mapr-version: 6.0.0.44429.BETA
44429:e7073547c8a7fd5262b96 2017-08-02 18:55:35,2082 ERROR JniCommon
fs/client/fileclient/cc/jni_MapRClient.cc:701 Thread: 47421 Client
initialization failed.
```

There are a few ways to fix this.

First make sure that the MapR version in your `pom.xml` file (or the one installed with the
package distribution) matches your installed MapR version.
After changing, rebuild/reinstall from source using the above steps.

A simple way to synchronize the .jar files from an existing MapR installation to the
jars used to build this module is to run the following steps -- note that this requires 
that you are building the package with at least the ```mapr-client``` package installed.

```
# git clone https://github.com/mapr-demos/python-bindings
# cd python-bindings
# python3 setup.py build
# for j in build/lib/maprdb/dependency/*.jar; do F=$(basename $j) ; if [ -f /opt/mapr/lib/$F ]; then cp /opt/mapr/lib/$F build/lib/maprdb/dependency/; fi done
# sudo python3 setup.py install
```




