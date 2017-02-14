# python-bindings
This package supplies the source code for the Python bindings for the MapR Open JSON Application Interface.  More information on OJAI can be found [here](https://www.mapr.com/blog/faster-application-development-open-json-application-interface-ojai).

## Quickstart

The package was tested on a Centos 7.2 system but the installation instructions and functionality are likely similar on others.  The below instructions assume 'python3' and 'pip3' are used to select the Python 3 tools in your environment.  If you do not have parallel Python 2 and Python 3 installations you may only need to use 'python' and 'pip'.

### Installing prerequisites

Requirements:

  - Python 3 and pip 3
  - Maven - `mvn` command should be in PATH.
  - GCC-c++ and python headers could be required to build dependencies

If your package manager is setup correctly, you can satisfy these dependencies with:

```
sudo yum install python34 python34-pip python34-devel gcc gcc-c++ wget
sudo wget http://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo -O /etc/yum.repos.d/epel-apache-maven.repo
sudo yum install apache-maven
```

### Configuring the connection to a MapR cluster

Ensure that you have the correct MapR configuration on the machine where you are running this software.  If you are running scripts on a MapR node, no additional steps are necessary.  If you are running scripts on a non-MapR node and want to attach to a MapR cluster, an easy way to get a base client configuration is to install the 'mapr-client' package as follows.  

```
sudo yum install mapr-client
```
Alternatively, a pre-configured Docker container client is available [https://www.mapr.com/blog/getting-started-mapr-client-container](with instructions here).

Whether or not you install the above package, at a minimum you must create and/or edit the file '/opt/mapr/conf/clusters.conf' and add the name of your cluster followed by the CLDB node and port.  For example, if your cluster name is demo.mapr.com and the CLDB node is 'maprdemo', you should have a single line in this file that looks like:

```
demo.mapr.com maprdemo:7222
```
And an entry in '/etc/hosts'/ for the 'maprdemo' hostname.  The [http://mapr.com/download](MapR Sandbox) is configured with the names used here.

### Option 1:  Installing from packages

Install the package via 'pip3' as follows.  This is an unbuilt source distribution and may take a few minutes to gather dependencies.

```
sudo pip3 install maprdb
```
Note that this may take several minutes.

### Option 2:  Installing from source

Alternatively, you can install this package from source. To do it, clone this repository and run the installer as follows:

```
git clone https://github.com/mapr-demos/python-bindings
cd python-bindings
sudo python3 setup.py install
```

Note that the setup script requires `setuptools`. You can find more information about how to install `setuptools` here:

https://pypi.python.org/pypi/setuptools

With the source installation you have the option of running the unit tests.  First ensure that 'pytest' is installed, then run the tests as follows.  You must have configured your MapR connection in the above steps for this to complete successfully.

```
sudo pip3 install pytest
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
