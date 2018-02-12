# coding=utf-8
"""
    vscsi reader for vscsi trace

    Author: Jason Yang <peter.waynechina@gmail.com> 2016/06

"""

from PyMimircache.cacheReader.abstractReader import AbstractReader
from PyMimircache.const import ALLOW_C_MIMIRCACHE, INSTALL_PHASE

if ALLOW_C_MIMIRCACHE and not INSTALL_PHASE:
    import PyMimircache.CMimircache.CacheReader as c_cacheReader


class VscsiReader(AbstractReader):
    """
    VscsiReader for vscsi trace
     
    """
    all = ["read_one_req", "read_time_req", "read_complete_req",
           "get_average_size", "get_timestamp_list",
           "reset", "copy", "get_params"]

    def __init__(self, file_loc, data_type='l',
                 block_unit_size=0, disk_sector_size=512, open_c_reader=True):
        """
        :param file_loc:            location of the file
        :param data_type:           type of data, can be "l" for int/long, "c" for string
        :param block_unit_size:     block size for storage system, 0 when disabled
        :param disk_sector_size:    size of disk sector
        :param open_c_reader:       bool for whether open reader in C backend
        """
        super().__init__(file_loc, data_type='l',
                         block_unit_size=block_unit_size,
                         disk_sector_size=disk_sector_size,
                         open_c_reader=open_c_reader)

        if ALLOW_C_MIMIRCACHE and open_c_reader:
            self.cReader = c_cacheReader.setup_reader(file_loc, 'v', data_type=data_type,
                                                                 block_unit_size=block_unit_size,
                                                                 disk_sector_size=disk_sector_size)
        self.support_size = True
        self.support_real_time = True

        self.get_num_of_req()

    def reset(self):
        """
        reset reader to initial state

        """
        if self.cReader:
            c_cacheReader.reset_reader(self.cReader)

    def read_one_req(self):
        """
        read one request, return only LBA
        :return: a long int indicating LBA
        """

        r = c_cacheReader.read_one_req(self.cReader)
        if r and self.block_unit_size != 0 and self.disk_sector_size != 0:
            r = r * self.disk_sector_size // self.block_unit_size
        return r

    def read_time_req(self):
        """
        return real_time information for the request in the form of (time, request)
        :return: a tuple of (time, request)
        """

        r = c_cacheReader.read_time_req(self.cReader)
        if r and self.block_unit_size != 0 and self.disk_sector_size != 0:
            r[1] = r[1] * self.disk_sector_size // self.block_unit_size
        return r

    def read_complete_req(self):
        """
        obtain more info for the request in the form of (time, request, size)
        :return: a tuple of (time, request, size)
        """

        r = c_cacheReader.read_complete_req(self.cReader)
        if r and self.block_unit_size != 0 and self.disk_sector_size != 0:
            r = list(r)
            r[1] = r[1] * self.disk_sector_size // self.block_unit_size
        return r

    def get_average_size(self):
        """
        sum sizes for all the requests, then divided by number of requests
        :return: a float of average size of all requests
        """

        sizes = 0
        counter = 0

        t = self.read_complete_req()
        while t:
            sizes += t[2]
            counter += 1
            t = self.read_complete_req()
        self.reset()
        return sizes / counter

    def get_timestamp_list(self):
        """
        get a list of timestamps
        :return: a list of timestamps corresponding to requests
        """

        ts_list = []
        r = c_cacheReader.read_time_req(self.cReader)
        while r:
            ts_list.append(r[0])
            r = c_cacheReader.read_time_req(self.cReader)
        return ts_list

    def copy(self, open_c_reader=False):
        """
        reader a deep copy of current reader with everything reset to initial state,
        the returned reader should not interfere with current reader

        :param open_c_reader: whether open_c_reader_or_not, default not open
        :return: a copied reader
        """

        return VscsiReader(self.file_loc, self.data_type,
                           self.block_unit_size, self.disk_sector_size, open_c_reader=open_c_reader)

    def get_params(self):
        """
        return all the parameters for this reader instance in a dictionary
        :return: a dictionary containing all parameters
        """

        return {
            "file_loc": self.file_loc,
            "data_type": self.data_type,
            "block_unit_size": self.block_unit_size,
            "disk_sector_size": self.disk_sector_size,
            "open_c_reader": self.open_c_reader
        }

    def __next__(self):  # Python 3
        super().__next__()
        element = self.read_one_req()
        if element is not None:
            return element
        else:
            raise StopIteration

    def __repr__(self):
        return "vscsiReader of {}".format(self.file_loc)
