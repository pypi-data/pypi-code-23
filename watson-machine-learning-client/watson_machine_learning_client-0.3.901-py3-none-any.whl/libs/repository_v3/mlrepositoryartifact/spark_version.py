################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *

lib_checker = LibraryChecker()
if lib_checker.installed_libs[PYSPARK]:
    from pyspark import SparkContext, SparkConf

class SparkVersion(object):
    @staticmethod
    def significant():
        lib_checker.check_lib(PYSPARK)
        conf = SparkConf()
        sc = SparkContext.getOrCreate(conf=conf)
        version_parts = [int(version_part) for version_part in sc.version.split('.')]
        return "{}.{}".format(version_parts[0], version_parts[1])