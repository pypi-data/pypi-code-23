# Copyright (c) 2018, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Module handling folder trees.
"""

import os
import re
import glob

from datetime import datetime

import pandas as pd


class SmartPath(object):

    """
    Base class for the single path structure to a data set.
    - allows building a path,
    - searching files with temporal slicing,
    - creating a pandas.DataFrame from a folder
    """

    def __init__(self, levels, hierarchy, make_dir=False):
        """

        Parameters
        ----------
        levels : list of str
            Name of level in hierarchy
        hierarchy : list of str
            List defining the order of the levels
        make_dir : bool, optional
            if set to True, then the full path of
            the SmartPath is created in the filesystem (default: False).
        """
        self.levels = levels
        self.hierarchy = hierarchy

        directory = self.build_levels()
        self.directory = directory

        if make_dir:
            self.make_dir()

    def __getitem__(self, level):
        """
        Short link for path, down to 'level'.
        Usage: path2level = your_smart_path[level]

        Parameters
        ----------
        level : str
            Name of level in hierarchy

        Returns
        -------
        path : str
            Path from root to level.
        """
        return self.get_level(level)

    def get_dir(self, make_dir=False):
        """
        Get directory.

        Parameters
        ----------
        make_dir : bool, optional
            Create directory if not exists (default: False).

        Returns
        -------
        folder : str
            Full path of the SmartPath
        """
        if make_dir:
            self.make_dir()

        return self.directory

    def make_dir(self):
        """
        Creates directory from root to deepest level
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def build_levels(self, level='', make_dir=False):
        """

        Parameters
        ----------
        level : str, optional
            Name of level in hierarchy
        make_dir : bool, optional
            creates the directory until level

        Returns
        -------
        path : str
            Full path of the SmartPath
        """
        directory = ''

        for h in self.hierarchy:
            if self.levels[h] is None:
                break
            else:
                directory = os.path.join(directory, self.levels[h])
                if h == level:
                    break

        if make_dir:
            if not os.path.exists(directory):
                os.makedirs(directory)

        return directory

    def get_level(self, level):
        """
        Get level.

        Parameters
        ----------
        level : str
            Name of level in hierarchy.

        Returns
        -------
        path : str
            Path from root to level.
        """
        if level in self.hierarchy:
            return self.build_levels(level=level)
        else:
            print('\'{}\' is not part of the path\'s hierarchy. '
                  'Try on of {}.'.format(level, self.hierarchy))


    def remove_level(self, level):
        '''
        In the SmartPath-instance, it removes a level from the hierarchy
        and level dictionary.

        Parameters
        ----------
        level : str
            Name of level in hierarchy.
        '''

        if level in self.hierarchy:

            self.levels.pop(level)
            self.hierarchy.remove(level)

            self.__init__(self.levels, self.hierarchy)

        else:
            print('Level \'{}\' is not in hierarchy!')

    def rebase_onto_root(self, root):
        '''
        Adds as first level 'root' to the SmartPath-instance.

        Parameters
        ----------
        root : str
            String of the root directory
        '''

        if 'root' in self.hierarchy:
            self.remove_level('root')

        self.levels.update({'root': root})
        self.hierarchy = ['root'] + self.hierarchy

        self.__init__(self.levels, self.hierarchy)


    def expand_full_path(self, level, files):
        """
        Joins the path at level with given filenames.

        Parameters
        ----------
        level : str
            Name of level in hierarchy.
        files : list of str
            List of file names.

        Returns
        -------
        path : str
            Full file path.
        """
        return [os.path.join(self[level], f) for f in files]


    def search_files(self, level, pattern='', full_paths=False):
        """
        Searches files meeting the regex pattern at level in the SmartPath

        Parameters
        ----------
        level : str
            Name of level in hierarchy
        pattern : str, optional
            string search pattern for file search (default: '')
        full_paths : bool, optional
            If True, full paths will be included in dataframe (default: False)

        Returns
        -------
        filenames : list of str
            File names at the level.
        """

        pattern = patterns_2_regex(pattern)

        paths = glob.glob(os.path.join(self.build_levels(level), '*.*'))
        basenames = reduce_2_basename(paths)

        regex = re.compile(pattern)
        files = [f for f in basenames if regex.match(f)]

        if full_paths:
            files = self.expand_full_path(level, files)

        return files

    def search_files_ts(self, level, pattern='',
                        date_position=1, date_format='%Y%m%d_%H%M%S',
                        starttime=None, endtime=None, full_paths=False):
        """
        Function searching files at a level in the SmartPath,
        returning the filenames and the datetimes as pd.DataFrame

        Parameters
        ----------
        level : str
            name of level in hierarchy
        pattern : str, optional
            string search pattern for file search
        date_position : int
            position of first character of date string in name of files
        date_format : str
            string with the datetime format in the filenames.
            e.g. '%Y%m%d_%H%M%S' reflects '20161224_000000'
        starttime : str or datetime, optional
            earliest date and time, if str must follow "date_format"
        endtime : str or datetime, optional
            latest date and time, if str must follow "date_format"
        full_paths : bool, optional
            should full paths be in the dataframe? if not set: False

        Returns
        -------
        df : pandas.DataFrame
            Dataframe holding the filenames and the datetimes
        """

        pattern = patterns_2_regex(pattern)

        files = self.search_files(level, pattern=pattern)
        times = extract_times(
            files, date_position=date_position, date_format=date_format)

        if full_paths:
            files = self.expand_full_path(level, files)

        df = pd.DataFrame({'Files': files}, index=times)
        df.sort_index(inplace=True)

        if (starttime is not None) or (endtime is not None):
            if not isinstance(starttime, datetime):
                starttime = datetime.strptime(starttime, date_format)
            if not isinstance(endtime, datetime):
                endtime = datetime.strptime(endtime, date_format)
            df = df[starttime:endtime]

        return df


class SmartTree(object):
    '''
    Class for collecting multiple SmartPaths() at one root path.
    '''

    def __init__(self, root, hierarchy, make_dir=False):
        '''

        Parameters
        ----------
        root : str
            directory path to root of directory tree.
        hierarchy : list of str
            List defining the order of the levels
        make_dir : bool, optional
            creates the root directory
        '''

        if not os.path.exists(root) and make_dir == False:
            raise OSError('Given directory for attribute \'root\', '
                          '\'{}\', does not exist!'.format(root))

        self.root = root
        self.dirs = {}
        self.hierarchy = hierarchy

        if make_dir:
            if not os.path.exists(self.root):
                os.makedirs(self.root)


    def __getitem__(self, pattern):
        '''
        Shortcut for get_smartpath()

        Usage-example: smarttree['C1003', 'E048N012T6']
        '''

        return self.get_smartpath(pattern)


    def add_smartpath(self, smartpath, make_dir=False):
        '''
        Adds a SmartPath-object to the SmartTree.

        Parameters
        ----------
        smartpath : SmartPath
            A SmartPath object. Only valid if hierarchy is compatible with the
            hierarchy of the SmartTree.
        make_dir : bool, optional
            creates the full directory of the SmartPath
        '''

        if isinstance(smartpath, SmartPath):

            smartpath.rebase_onto_root(self.root)

            if self.hierarchy == smartpath.hierarchy:

                self.dirs.update({smartpath.get_dir(): smartpath})

            else:
                print("SmartPath is not compatible with SmartTree: "
                      "Hierarchies do not correspond!")

            if make_dir:
                smartpath.make_dir()


    def remove_dir(self, key):
        '''
        Removes the SmartPath with 'key' from the SmartTree

        Parameters
        ----------
        key : str
            Path representing the key for the SmartPath
        '''

        self.dirs.pop(key)


    def make_dirs(self):
        '''
        Creates a full path for each of the contained SmartPaths.
        '''

        for _, smartpath in self.dirs.items():
            smartpath.make_dir()


    def get_smartpath(self, pattern):
        '''
        Returns one SmartPath-object from the SmartTree that matches with
        the pattern. If more than one match, None is returned.

        Parameters
        ----------
        pattern : str, optional
            string search pattern for file search

        Returns
        -------
        SmartPath
            The path object matching the pattern.
        '''

        pattern = patterns_2_regex(pattern)

        paths = self.dirs.keys()

        matching_paths = []

        regex = re.compile(pattern)
        matching_paths += [m for m in paths if regex.match(m)]

        if len(matching_paths) == 0:
            return None
        elif len(matching_paths) > 1:
            return None
        else:
            return self.dirs[matching_paths[0]]


    def collect_level(self, level, pattern=None):
        '''
        Returns a list of paths at given level.

        Parameters
        ----------
        level : str
            name of level in hierarchy
        pattern : str, optional
            string search pattern for file search
        Returns
        -------
        list of str
            unique set of paths at given level, matching the given pattern
        '''

        result = []

        for _, smartpath in self.dirs.items():
            if smartpath.levels[level] is not None:

                if pattern is not None:
                    if smartpath.levels[level] == pattern:
                        result.append(smartpath[level])
                else:
                    result.append(smartpath[level])

        return set(result)


def build_smarttree(root, hierarchy):
    '''
    Function walking through directories in root path for
    building a structure of/for SmartPaths

    Parameters
    ----------
    root
    hierarchy

    Returns
    -------

    '''

    pass

def reduce_2_basename(files):
    """
    Converts full file paths to file base names.

    Parameters
    ----------
    files : list of str
        list of filepaths

    Returns
    -------
    filenames : list of str
        List of base file names.
    """
    return [os.path.basename(f) for f in files]


def extract_times(files, date_position=1, date_format='%Y%m%d_%H%M%S'):
    """
    Extracts the datetimes from filenames.

    Parameters
    ----------
    files : list of str
        list of strings with filenames or filepaths
    date_position : int
        position of first character of date string in name of files
    date_format: str
        string with the datetime format in the filenames.
        '%Y%m%d_%H%M%S' reflects eg. '20161224_000000'

    Returns
    -------
    times : list of datetime
        List of datetime objects extracted from the filenames.
    """
    if any([os.path.isdir(x) for x in files]):
        files = reduce_2_basename(files)

    times = []
    for f in files:
        t = datetime.strptime(
            f[date_position:date_position + len(date_format) + 2],
            date_format)
        times.append(t)

    return times


def patterns_2_regex(patterns):
    '''
    Converts any string, or tuple of strings, to a regex pattern.

    Parameters
    ----------
    patterns : str or tuple of str
        String patterns

    Returns
    -------
    str: regex string
    '''

    if isinstance(patterns, str):
        patterns = [patterns]

    regex = ''

    for p in patterns:
        regex += '.*{}'.format(p)

    return regex


if __name__ == '__main__':
    pass