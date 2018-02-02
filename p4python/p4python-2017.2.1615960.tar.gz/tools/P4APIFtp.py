from __future__ import print_function
import platform

import tarfile
import tempfile
import re
import os, os.path
from ftplib import FTP, error_perm
import itertools
from .Version import Version

PERFORCE_FTP = 'ftp.perforce.com'
# user is anonymous, no need to log on with a special user


class P4APIFtp:
    def __init__(self):
        self.ftp = FTP(PERFORCE_FTP)
        self.pattern = re.compile(r'(?P<permissions>[ld-][r-][w-][x-][r-][w-][x-][r-][w-][x-])' + \
                                  r'\s+\d+\s+\w+\s+\w+\s+\d+\s+' + \
                                  r'(?P<date>\S+\s+\S+\s+\S+)\s+' + \
                                  r'(?P<name>.+)')
        self.platform = self.findPlatform

    @property
    def findPlatform(self):
        """
        We are looking for out platform following the Perforce naming standard,
        i.e. bin.xxxyyy
        :return: the platform we are on
        """

        architecture = platform.architecture()[0]  # 32bit or 64bit
        machine = platform.machine()
        system = platform.system()
        uname = platform.uname()

        platform_str = "bin."

        if system == "Linux":
            platform_str += "linux26"
            if machine in ['i386', 'i586', 'i686', 'x86']:
                platform_str += "x86"
            elif machine in ['x86_64', 'amd64']:
                platform_str += "x86_64"
            elif machine in ['armv6l']:
                platform_str += 'armhf'
            else:
                raise Exception("Unknown machine {}. Please configure P4API manually".format(machine))

        elif system == "Windows":
            platform_str = platform_str + "NT"
            if architecture == "32bit":
                platform_str += "X86"
            else:
                platform_str += "X64"

        elif system == "Darwin":
            platform_str = platform_str + "darwin90" + machine

        elif system == "FreeBSD":
            platform_str += "freebsd"
            release = uname.release

            value = int(''.join(itertools.takewhile(lambda s: s.isdigit(), release)))

            if value >= 10:
                platform_str += "100"
                if machine == 'amd64':
                    platform_str += "x86_64"
                elif machine == 'i386':
                    platform_str += "x86"
                else:
                    raise Exception("Unknown machine {}. Please configure P4API manually".format(machine))


        else:
            raise Exception(
                "System {} is not supported for automatic download. Please configure P4API manually".format(system))

        return platform_str

    def sortedDirectories(self, dirs):
        # first, extract the directory names from the list output
        names = [self.pattern.match(x).group('name') for x in dirs]

        # sort them by date, avoiding the Y2K problem
        sorted_names = sorted(names, key=lambda x: '19' + x if x[1] == '9' else '20' + x, reverse=True)

        return sorted_names

    def descend(self, d):
        pwd = self.ftp.pwd()
        apidir = None
        tar = None

        try:
            self.ftp.cwd(d)
            self.ftp.cwd(self.platform)

            p4api = 'p4api.tgz'
            tempdir = tempfile.gettempdir()
            filename = os.path.join(tempdir, p4api)
            with open(filename, 'wb') as f:
                self.ftp.retrbinary('RETR ' + p4api, f.write)

            tar = tarfile.open(filename, 'r')
            apidir = os.path.join(tempdir, tar.getnames()[0])

            # if apidir exists, don't unpack again, otherwise read-only errors will occur
            if not (os.path.exists(apidir) and os.path.isdir(apidir)):
                tar.extractall(tempdir)
        except error_perm as e:
            return None
        finally:
            self.ftp.cwd(pwd)

            if tar:
                tar.close()

        return apidir

    def findAPI(self, names, version):
        """
        Searches through the provided list of directories depth first.
        :param names:
        :return: The path to the API dir or None
        :return: The path to the API dir or None
        """

        # start with the first one
        #   drill down in the directory
        #   find the correct platform
        #   descend into the platform directory
        #   see if we can find p4api.tgz
        #   otherwise, use next dated directory and start over

        for d in names:
            try:
                dirVersion = Version(d)
                if dirVersion > version:
                    continue
                apidir = self.descend(d)
                if apidir:
                    return apidir
            except:
                pass

        return None

    def loadAPI(self, version):
        self.ftp.connect()
        self.ftp.login()
        self.ftp.cwd("perforce")

        dirs = []
        self.ftp.retrlines("LIST", lambda str: dirs.append(str))

        s = self.sortedDirectories(dirs)
        return self.findAPI(s, version)