# -*- coding: utf-8 -*-
import io
import json
import logging
import hashlib
import urllib
from PIL import Image
from io import BytesIO
from ..module import append_paths, exists
from os import makedirs

from pandas import DataFrame, Series
from pandas import read_csv, read_json
from pynlple.data.source import Source
from pynlple.exceptions import DataSourceException


class DataframeSource(Source):

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe


class TsvDataframeSource(Source):

    def __init__(self, dataframe_path, separator='\t', quote=0, escape_char='\\', column_names=None, fill_na_map=None, encoding='utf-8', index_columns=None):
        self.path = dataframe_path
        self.separator = separator
        self.column_names = column_names
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_columns = index_columns
        self.quote = quote
        self.escape_char = escape_char

    def get_dataframe(self):
        #TODO: Eats \r\n and spits sole \n in literal value strings instead
        if self.column_names:
            header = None
            names = self.column_names
        else:
            header = 'infer'
            names = None
        dataframe = read_csv(self.path,
                             sep=self.separator,
                             header=header,
                             names=names,
                             quoting=self.quote,
                             escapechar=self.escape_char,
                             encoding=self.encoding)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from ' + self.path)
        return dataframe

    def set_dataframe(self, dataframe):
        if self.column_names:
            names = self.column_names
        else:
            names = True
        dataframe.to_csv(self.path,
                         sep=self.separator,
                         header=names,
                         quoting=self.quote,
                         escapechar=self.escape_char,
                         encoding=self.encoding)
        print('Write: ' + str(len(dataframe.index)) + ' rows to ' + self.path)


class JsonFileDataframeSource(Source):

    FILE_READ_METHOD = 'rt'
    FILE_WRITE_METHOD = 'wt'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, json_file_path, fill_na_map=None, index_columns=None):
        self.json_file_path = json_file_path
        self.na_map = fill_na_map
        self.index_columns = index_columns

    def get_dataframe(self):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_READ_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            #TODO: implement fill_na_map
            df = read_json(data_file, orient='records', encoding=JsonFileDataframeSource.DEFAULT_ENCODING)
        return df

    def set_dataframe(self, dataframe):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_WRITE_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            #TODO: implement fill_na_map
            json.dump(dataframe.reset_index().to_dict(orient='records'), data_file, ensure_ascii=False, indent=2)


class JsonDataframeSource(Source):

    def __init__(self, json_source, keys=None, fill_na_map=None, index_columns=None):
        self.json_source = json_source
        self.keys = keys
        self.na_map = fill_na_map
        self.index_columns = index_columns

    def get_dataframe(self):
        extracted_entries = list()
        for json_object in self.json_source.get_data():
            entry = dict()
            if self.keys:
                for key in self.keys:
                    if key not in json_object:
                        entry[key] = self.na_map[key]
                    else:
                        entry[key] = json_object[key]
            else:
                for key in json_object:
                    entry[key] = json_object[key]
                if self.na_map:
                    for key, value in self.na_map:
                        if key not in entry:
                            entry[key] = value
            extracted_entries.append(entry)
        dataframe = DataFrame(extracted_entries)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from jsonsource')
        return dataframe

    def set_dataframe(self, dataframe):
        entries = dataframe.reset_index().to_dict(orient='records')
        for entry in entries:
            if self.keys:
                for key in list(entry.keys()):
                    if key not in self.keys:
                        entry.pop(key, None)
            if self.na_map:
                for key, value in self.na_map:
                    if key not in entry:
                        entry[key] = value
        self.json_source.set_data(entries)


class UrlImageCachingDFSource(object):

    logger = logging.getLogger(__name__)

    COLUMN_NAME_PREFIX = 'path:'

    def __init__(self, dataframe_source, url_columns, cache_folder, content_type=['image'], reload_content=False, timeout=15, log_every=100):
        self.df_source = dataframe_source
        self.url_columns = url_columns
        self.cache_folder = cache_folder
        self.content_type = content_type
        self.reload_content = reload_content
        self.timeout = timeout
        self.log_every = log_every

    def get_dataframe(self):
        dataframe = self.df_source.get_dataframe()
        for col in self.url_columns:
            if col not in dataframe.columns:
                raise DataSourceException('Column {} with urls not found in dataframe {}'.format(col, repr(self.df_source)))
        for col in self.url_columns:
            column = dataframe.loc[:,col]
            new_col = UrlImageCachingDFSource.COLUMN_NAME_PREFIX + col
            image_paths = self.load(column.tolist(), self.cache_folder)
            dataframe[new_col] = Series(image_paths)
        return dataframe

    def load(self, urls, folder):
        image_paths = []
        for i_, url in enumerate(urls):
            if self.log_every and ((i_ % self.log_every) == 0):
                self.logger.info('[%s] loading url contents (%d/%d).', str(self.__class__.__name__), i_, len(urls))
            if not exists(folder):
                makedirs(folder)
            if url and type(url) is str and len(url) > 0:
                image_path = self.__check_and_download(url, folder, str(hashlib.sha1(url.encode('utf-8')).hexdigest()))
                image_paths.append(image_path)
            else:
                self.logger.debug('[%s] entry num %s skipped. No valid url found: %s', str(self.__class__.__name__), i_, str(url))
                image_paths.append(None)
        return image_paths

    def __check_and_download(self, url, target_folder, target_name):
        file_path = append_paths(target_folder, target_name+'.jpg')
        if self.reload_content or not exists(file_path):
            try:
                url_obj = urllib.request.urlopen(url, timeout=self.timeout)
                if not self.content_type or url_obj.headers.get_content_maintype() in self.content_type:
                    self.logger.debug('[%s] Url: %s. Downloading entry.', str(self.__class__.__name__), url)
                    img = Image.open(BytesIO(url_obj.read()))
                    rgb_img = img.convert('RGB')
                    rgb_img.save(file_path)
                    url_obj.close()
                    return file_path
                else:
                    self.logger.warn('[%s] entry is skipped as non-%s: %s. Url: %s',
                                     str(self.__class__.__name__), repr(self.content_type),
                                     url_obj.headers.get_content_maintype(), url)
                    return None
            except Exception as e:
                self.logger.error('[%s] Image url %s failed to load:\n%s', str(self.__class__.__name__), url, str(e))
                return None
        else:
            self.logger.debug('[%s] entry exists. Url: %s. Skipping downloading.', str(self.__class__.__name__), url)
            return file_path

    def set_dataframe(self, dataframe):
        self.df_source.set_dataframe(dataframe)