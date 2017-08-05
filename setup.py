import glob
import platform
import os
from setuptools import setup
import subprocess


# Retrieve JARs
dependencies_dir = os.path.join(os.path.dirname(__file__), "maprdb", "dependency", "*.jar")
if len(glob.glob(dependencies_dir)) == 0:  # __init__.py
    code = subprocess.call(["mvn", "dependency:copy-dependencies"], shell=platform.system() == "Windows")
    if code:
        exit(code)


setup(
    name = "maprdb",
    version = "0.0.3",
    description = ("API to work with MapR DB. Wrapper of Java API."),
    license = "Apache License 2.0",
    keywords = "mapr db json",
    packages=["maprdb", "maprdb.dependency"],
    classifiers=[
        "Topic :: Utilities",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: Apache Software License"
    ],
    install_requires=[
        "JPype1==0.6.1",
        "multipledispatch"
    ],

    package_data={
        "maprdb.dependency": ['*.jar'],
    }
)
