import os
import subprocess
"""
Release database
"""
class ReleaseDatabase(object):
    ins = None

    @classmethod
    def instance(cls):
        """ Return the database itself
        """
        if cls.ins is None:
            cls.ins = ReleaseDatabase()
        return cls.ins


    def get_env(self, release):
        env = os.environ
        # subprocess.Popen("").wait()
        return env

releasedb = ReleaseDatabase.instance()
