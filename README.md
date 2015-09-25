# python-bindings
Python bindings for MapR DB JSON API

# How to Build
Requirements:

  - Python 3
  - Maven - `mvn` command should be in PATH.
  - GCC and python headers could be required to build dependencies

To install this package run

    python setup.py install

# Running unit tests

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
