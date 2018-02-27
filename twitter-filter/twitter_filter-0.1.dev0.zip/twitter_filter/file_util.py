# -*- coding: utf-8 -*-
"""

This module is responsible for every file operation that occurs
in the application, and its supporting functionalities like
checking the existence of a directory or a file and reading
different formats like csv files.

"""

import csv
import io
import os
from pathlib import Path

import pandas

from twitter_filter.exceptions_wrapper import ErrorWrapper


# this class handles interacting with files
class FileUtil:
    """ This is base class for my application file operations.

    This class implements reading and writing from/to files, reading
    csv files and checking directories.

    """
    def __init__(self):
        pass

    @staticmethod
    def write_item(file_path, line):
        """
        This function writes a line to file.


        Parameters
        ----------
        file_path : str
            The write file path.
        line : str
            The item we want to write on a line in the file.

        Returns
        -------

        """
        try:
            f = io.open(file_path, 'a', encoding="utf-8")
            f.write(line)
            f.close()
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def check_directory(file_path):
        """
        This function checks the existence of a directory
        and creates it if it is not existent.


        Parameters
        ----------
        file_path : str
            The file path.

        Returns
        -------

        """
        try:
            the_dir_path = file_path.split('/')
            if len(the_dir_path) > 1:
                file_name = the_dir_path[len(the_dir_path)-1]
                the_directory = file_path[:-len(file_name)]
                if not os.path.exists(the_directory):
                    path = Path(the_directory)
                    path.mkdir(parents=True)
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def write_to_file(file_path, lines):
        """
        This function writes a list to a file in the file_path.

        Parameters
        ----------
        file_path : str
            The file path.
        lines : list
            The lines we want to write to the file.

        Returns
        -------

        """
        try:
            FileUtil.check_directory(file_path)
            f = io.open(file_path, 'a', encoding="utf-8")
            for n, line in enumerate(lines):
                if line.startswith(" "):
                    lines[n] = "" + line.rstrip()
                else:
                    lines[n] = line.rstrip()
                f.write(u''.join(line+'\n'))
            f.close()
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def file_reader(file_path):
        """
        This function reads a file in the file_path
        and returns a list of its lines.

        Parameters
        ----------
        file_path : str
            The file path.

        Returns
        -------

        """
        try:
            f = open(file_path, encoding="utf-8", buffering=(2 << 16) + 8)
            lines = f.read().splitlines()
            return lines
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def csv_reader(file_path, columns_names, index_col_name):
        """
        This function reads a csv file in the file_path
        and returns a list of its lines.

        Parameters
        ----------
        file_path : str
            The file path.
        columns_names : list
            The columns names you want to read.
        index_col_name : str
            The index column name.

        Returns
        -------

        """
        try:
            csv_file = pandas.read_csv(file_path, sep="[,]", lineterminator='\n', engine='python', header=None, names=columns_names, index_col=index_col_name, quoting=csv.QUOTE_NONE)
            rows = [tuple(x) for x in csv_file.values]
            rows = rows[1:]
            rows = [(day,) + x for x, day in zip(rows, list(csv_file.index.values)[1:])]
            return rows
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def append_files(read_file_path, write_file_path):
        """
        This function appends the file in read_file_path lines
        to the file in write_file_path.

        Parameters
        ----------
        read_file_path : str
            The read file path.
        write_file_path : str
            The write file path.

        Returns
        -------

        """
        try:
            appended_file_lines = FileUtil.file_reader(read_file_path)
            FileUtil.write_to_file(write_file_path, appended_file_lines)
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def chunks(list_to_chunk, num_of_lines_per_chunk):
        """Yield successive num_of_lines_per_chunk-sized chunks from list_to_chunk."""
        for i in range(0, len(list_to_chunk), num_of_lines_per_chunk):
            yield list_to_chunk[i:i + num_of_lines_per_chunk]

    @staticmethod
    def write_to_file_chunks(file_path, lines, chunk_size=100):
        """
        This function writes a list to a file in the file_path.
        It divides the file lines into chunks and writes the chunks
        instead of writing individual lines.

        Parameters
        ----------
        file_path : str
            The file path.
        lines : list
            The lines we want to write to the file.
        chunk_size : int or 100
            The chunk size to write in one IO operation.

        Returns
        -------

        """
        try:
            FileUtil.check_directory(file_path)
            f = io.open(file_path, 'a', encoding="utf-8")
            if len(lines) < 100:
                lines = map(lambda x: x + '\n', lines)
                f.writelines(lines)
            else:
                chunks = list(FileUtil.chunks(lines, chunk_size))
                for chunk in chunks:
                    chunk = map(lambda x: x + '\n', chunk)
                    f.writelines(chunk)
            f.close()
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def get_immediate_subdirectories(directory_path):
        """
        This function gets the immediate subdirectories of the input directory.

        Parameters
        ----------
        directory_path : str
            The directory path.

        Returns
        -------
        list
            The immediate subdirectories names.

        """
        return [name for name in os.listdir(directory_path)
                if os.path.isdir(os.path.join(directory_path, name))]

    @staticmethod
    def get_immediate_files(directory_path):
        """
        This function gets the immediate files of the input directory.

        Parameters
        ----------
        directory_path : str
            The directory path.

        Returns
        -------
        list
            The immediate files names.

        """
        return [name for name in os.listdir(directory_path)
                if not os.path.isdir(os.path.join(directory_path, name))]

    @staticmethod
    def write_string(text, file_path):
        """
        This function writes a text into file.

        Parameters
        ----------
        text : str
            The text to write.
        file_path : str
            The output file path.

        Returns
        -------

        """
        FileUtil.check_directory(file_path)
        f = io.open(file_path, 'w', encoding="utf-8")
        f.write(text)

