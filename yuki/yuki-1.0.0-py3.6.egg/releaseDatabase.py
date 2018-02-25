import cepcenv
import subprocess
"""
Release database
"""
class ReleaseDatabase(object):
    instance = None

    @classmethod
    def instance(cls):
        """ Return the database itself
        """
        if cls.instance is None:
            cls.instance = ReleaseDatabase()
        return cls.instance


    def get_env(release):
        env = {
        }
        # subprocess.Popen("").wait()
        return env

releasedb = ReleaseDatabase
