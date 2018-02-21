import os
import csv
import gzip
import json
import boto3
import codecs

import numpy as np
import pandas as pd

from . import qgservice
from .qgutils import *

from io import BytesIO
from datetime import datetime
from collections import OrderedDict

class QuantGoApi(object):
    index_bucket = 'as-data-index'
    default_store_format = '%(path)s/%(year)s/%(date)s/%(base)s/%(file)s'
    default_service = None
    debug = False
    
    def __init__(self, access_key=None, secret_key=None, profile_name=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.profile_name = profile_name
        
        self.session = boto3.Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, profile_name=self.profile_name)
    
    def list_services(self):
        """
        List available services from qgservice.py
        """
        attrs = qgservice.__dict__
        res = []
        for attr in attrs:
            attrv = getattr(qgservice, attr)
            if type(attrv) is dict and 'bucket' in attrv:
                res.append(attrv)
        return res
    
    def is_debug(self):
        """
        Check if debug mode enabled.
        API will print downloaded file names to console when debug is enabled.
        """
        return self.debug
    
    def set_debug(self, debug):
        """
        Enable/disable debug mode.
        API will print downloaded file names to console when debug is enabled.
        """
        self.debug = debug
    
    def set_default_service(self, service):
        """
        Sets default service. This service will be used when service parameter not passed (or set to None) to above functions
        :param service: quantgo service (from qgservice.py)
        """
        self.default_service = service
    
    def __check_service(self, service):
        """
        Validate service. Raise exception if invalid service passed
        """
        if not service or not isinstance(service, dict) or 'bucket' not in service:
            raise Exception('Invalid service. Use service from qgservice.py')
        return True
    
    def __validate_service(self, service):
        """
        Validate service or return default service when no service passed (or set to None)
        Only for internal class use
        :param service: quantgo service (from qgservice.py)
        """
        if service is None:
            service = self.default_service
        if service is None:
            raise Exception('Default service is not set')
        self.__check_service(service)
        return service
    
    def get_raw_file(self, file_name, bucket):
        """
        Read compressed file from bucket
        :param file_name: object key
        :param bucket: bucket name
        """
        # Get file
        s3 = self.session.client('s3')
        response=s3.get_object(Bucket=bucket, Key=file_name, RequestPayer='requester')
        # read compressed data
        compr_data = response['Body'].read()
        return compr_data
    
    def get_raw_uncompr_file(self, file_name, bucket):
        """
        Read uncompressed data from bucket, uncompress it and return as string.
        :param file_name: object key
        :param bucket: bucket name
        """
        # read compressed data
        compr_data = self.get_raw_file(file_name, bucket)
        # uncompress data
        with gzip.GzipFile(fileobj=BytesIO(compr_data)) as f:
            uncompr_data = f.read()
        return uncompr_data.decode("utf-8")
    
    def _build_index(self, service):
        """
        Build index key for service
        """
        if service["file_structure"] < 2:
            file_name = '%s/index.json.gz' % (service['bucket'])
        else:
            bucket = service['bucket'] % (service['start_year'])
            file_name = '%s/index.json.gz' % (bucket)
        return file_name
    
    def _build_symbols_index(self, date, service):
        """
        Build symbols index key for service
        """
        date = datetime.strptime(date, '%Y%m%d')
        if service["file_structure"] < 2:
            file_name = '%s/%s.csv.gz' % (service['bucket'], date.strftime('%Y%m%d'))
        else:
            bucket = service['bucket'] % (date.year)
            file_name = '%s/%s.csv.gz' % (bucket, date.strftime('%Y%m%d'))
        return file_name
    
    def _build_bucket_and_key(self, date, sym, service):
        """
        Build key and bucket name for service
        """
        # encode symbol name
        sym = self.encode_symbol(sym)
        # Convert tdate to object to validate date format
        date = datetime.strptime(date, '%Y%m%d')
        # Create keyname, eg. filename to download
        if service['file_structure'] == 0:
            # equities file structure: year/date/X/XXX.csv.gz
            key = '%d/%s/%s/%s.csv.gz' % (date.year, date.strftime('%Y%m%d'), sym[0], sym)
            bucket = service['bucket']
        elif service['file_structure'] == 1:
            # futures file structure: year/date/base/sym.csv.gz
            key = '%d/%s/%s/%s.csv.gz' % (date.year, date.strftime('%Y%m%d'), sym[0:-2], sym)
            bucket = service['bucket']
        elif service['file_structure'] == 2:
            key = '%s/%s/%s.csv.gz' % (date.strftime('%Y%m%d'), sym[0:-2], sym)
            bucket = service['bucket'] % (date.year)
        elif service['file_structure'] == 3:
            sym_parts = sym.split('!')
            key = '%s/%s/%s/%s.csv.gz' % (date.strftime('%Y%m%d'), sym[0], sym_parts[0], sym)
            bucket = service['bucket'] % (date.year)
        else:
            raise Exception('Unknown service file structure')
        return (bucket, key)
    
    def get_file(self, sym, date, service=None):
        """
        Read compressed data from bucket and return as string.
        :param sym: symbol name. '/' will be replaces with '_'
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        bucket, key = self._build_bucket_and_key(date, sym, service)
        return self.get_raw_file(key, bucket)

    def get_csv_file(self, sym, date, service=None):
        """
        Read compressed data from bucket, uncompress it and return as string.
        :param sym: symbol name. '/' will be replaces with '_'
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        # read compressed data
        compr_data = self.get_file(sym, date, service)
        # uncompress data
        with gzip.GzipFile(fileobj=BytesIO(compr_data)) as f:
            uncompr_data = f.read()
        return uncompr_data.decode("utf-8")
    
    def read_raw_file(self, file_name):
        """
        Read downloaded file into string. Data will be uncompressed if file if in .gz format
        :param file_name: downloaded file name
        """
        with open(file_name, 'rb') as f:
            data=f.read()
        if file_name.lower().endswith('.gz'):
            with gzip.GzipFile(fileobj=BytesIO(data)) as f:
                data = f.read()
        return data
    
    def get_multi_dataframe(self, files_list):
        """
        Read multiple downloaded files and convert into single dataframe
        :param files_list: list of file names
        :return: pandas dataframe
        """
        frames = []
        for file_name in files_list:
            data = self.read_raw_file(file_name)
            # Read data into Pandas dataframe
            df=pd.read_csv(BytesIO(data))
            # Set Index of DataFrame to be time column
            df.set_index('TimeBarStart')
            frames.append(df)
        if not frames:
            return None
        if len(frames) == 1:
            return frames[0]
        res = pd.concat(frames)
        df.set_index('TimeBarStart')
        return res
    
    def get_dataframe(self, sym, date, service=None):
        """
        Returns dataframe with date's data. Returns "None" if no data.
        :param sym: String for symbol
        :param tdate: Date for trade date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        :return: pandas dataframe
        """
        
        date = self.__convert_date(date)
        
        service = self.__validate_service(service)
        # read uncompressed data
        uncompr_data = self.get_csv_file(sym, date, service)
            
        # Read data into Pandas dataframe
        df=pd.read_csv(BytesIO(uncompr_data.encode()))
    
        # Set Index of DataFrame to be time column
        df.set_index('TimeBarStart')
    
        # return DataFrame
        return (df)
    
    def get_index(self, service=None):
        """
        Gets bucket index. Format: {year: [date...],...}
        :param service: quantgo service (from qgservice.py)
        :return: bucket index
        """
        service = self.__validate_service(service)
        file_name = self._build_index(service)
        s3 = self.session.client('s3')
        response=s3.get_object(Bucket=self.index_bucket, Key=file_name, RequestPayer='requester')
        compr_data = response['Body'].read()
        with gzip.GzipFile(fileobj=BytesIO(compr_data)) as f:
            uncompr_data = f.read()
        return json.loads(uncompr_data.decode('utf-8'), object_pairs_hook=OrderedDict)
    
    def list_years(self, service=None):
        """
        Gets list of trade years using index
        :param service: quantgo service (from qgservice.py)
        :return: list of trade years
        """
        service = self.__validate_service(service)
        years = []
        index = self.get_index(service)
        for key, _ in index.items():
            years.append(key)
        return years
    
    def list_trade_dates(self, year, service=None):
        """
        Gets list of trade dates for specific year using index
        :param year: YYYY (string or number)
        :param service: quantgo service (from qgservice.py)
        :return: list of trade dates
        """
        year = None if year is None else str(year)
        service = self.__validate_service(service)
        index = self.get_index(service)
        year = str(year)
        if year not in index:
            return []
        return index[year]
    
    def list_all_trade_dates(self, service=None):
        """
        Gets list of trade dates using index
        :param service: quantgo service (from qgservice.py)
        :return: list of trade dates
        """
        service = self.__validate_service(service)
        dates = []
        index = self.get_index(service)
        for _, value in index.items():
            dates.extend(value)
        return dates
    
    def list_range_trade_dates(self, start_date, end_date, service=None):
        """
        Gets list of trade dates in given range
        :param start_date: beginning date
        :param end_date: ending date
        :param service: quantgo service (from qgservice.py)
        :return: list of trade dates
        """
        start_date = self.__convert_date(start_date)
        end_date = self.__convert_date(end_date)
        all_dates = self.list_all_trade_dates(service)
        dates = []
        for date in all_dates:
            if ((start_date is None) or (date >= start_date)) and ((end_date is None) or (date <= end_date)):
                dates.append(date)
        return dates
    
    def get_symbols_index(self, date, service=None):
        """
        Gets symbols index.
        Old Format: {symbol: [bucket, path, file_name, compr_size, uncompr_size],...}
        New Format: {symbol: [bucket, path, file_name, compr_size, uncompr_size, date, symbol],...}
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        :return: bucket index
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        records = {}
        file_name = self._build_symbols_index(date, service)
        s3 = self.session.client('s3')
        try:
            response=s3.get_object(Bucket=self.index_bucket, Key=file_name, RequestPayer='requester')
        except Exception as e:
            if e.response['Error']['Code'] == "NoSuchKey" or e.response['Error']['Code'] == "404":
                raise Exception('Non-trading date')
            else:
                raise
        compr_data = response['Body'].read()
        with gzip.GzipFile(fileobj=BytesIO(compr_data)) as f:
            ureader = codecs.getreader("utf-8")
            contents = ureader( f )
            reader = csv.reader(contents, skipinitialspace=True, delimiter=',', quotechar='"')
            for row in reader:
                if len(row) <= 5:
                    # old formal. we have to decode symbol name from file name
                    symbol = self.decode_symbol('.'.join(row[2].split('.')[:-2])) # convert XXX_Y.csv.gz into XXX/Y
                else:
                    symbol = row[6]
                records[symbol] = row
        return records
    
    def get_symbols(self, date, service=None):
        """
        Gets symbols list
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        :return: list symbols
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        index = self.get_symbols_index(date, service)
        return list(index.keys())
    
    def get_base_futures(self, date, service=None):
        """
        Gets base futures
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        :return: list of base symbols
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        index = self.get_symbols_index(date, service)
        bases = []
        for _, value in index.items():
            path = value[1]
            base = path.split('/')[-1]
            if base not in bases:
                bases.append(base)
        return bases
    
    def get_futures_by_base(self, date, base, service=None):
        """
        Get list of futures for given date and base future
        :param date: trading date in YYYYMMDD format
        :param base: base future
        :param service: quantgo service (from qgservice.py)
        :return: list of futures
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        index = self.get_symbols_index(date, service)
        futures = []
        for key, value in index.items():
            path = value[1]
            fbase = path.split('/')[-1]
            if fbase == base:
                futures.append(key)
        return futures
    
    def get_futures_by_base_index(self, index, base):
        """
        Get list of futures for given date and base future
        :param index: symbols index
        :param base: base future
        :return: list of futures
        """
        futures = []
        for key, value in index.items():
            path = value[1]
            fbase = path.split('/')[-1]
            if fbase == base:
                futures.append(key)
        return futures
    
    def is_trade_date(self, date, service=None):
        """
        Check if given date is traded
        :param date: trading date in YYYYMMDD format
        """
        date = self.__convert_date(date)
        dates = self.list_all_trade_dates(service)
        return str(date) in dates
    
    def is_valid_symbol(self, date, symbol, service=None):
        """
        Check if symbol is valid for given date
        :param date: trading date in YYYYMMDD format
        :param symbol: symbol name
        :param service: quantgo service (from qgservice.py)
        :return: True if valid symbol
        """
        date = self.__convert_date(date)
        symbols = self.get_symbols_index(date, service)
        return symbol in symbols
    
    def is_valid_base_future(self, date, symbol, service=None):
        """
        Check if base future is valid for given date
        :param date: trading date in YYYYMMDD format
        :param symbol: base future
        :param service: quantgo service (from qgservice.py)
        :return: True if valid base
        """
        date = self.__convert_date(date)
        bases = self.get_base_futures(date, service)
        return symbol in bases
    
    def list_trade_date_symbols(self, date, service=None):
        """
        Gets list of symbols for trade date using index
        :param tdate: trading date in YYYYMMDD format
        :param service: quantgo service (from qgservice.py)
        :return: list of symbols
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        symbols = []
        index = self.get_symbols_index(date, service)
        for key, _ in index.items():
            symbols.append(key)
        return symbols
    
    def encode_symbol(self, symbol):
        """
        Encode symbol name. Replace '/' with '_' to be compatible with S3 directory structure
        :param symbol: symbol name
        :return: encoded symbol name
        """
        return symbol.replace('/', '_').replace(' ', '!')
    
    def decode_symbol(self, symbol):
        """
        Decode symbol name. Replace '_' with '/' to be compatible with S3 directory structure
        :param symbol: symbol name
        :return: encoded symbol name
        """
        return symbol.replace('_', '/').replace('!', ' ')
    
    def download_list(self, records, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of date-symbol pair
        :param records: list of date-symbol tuples
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        service = self.__validate_service(service)
        if not records:
            return []
        if store_format is None:
            store_format = self.default_store_format
        #'%(path)s/%(year)s/%(date)s/%(base)s/%(file)s'
        tasks = []
        result = []
        for rec in records:
            date = self.__convert_date(rec[0])
            tdate = datetime.strptime(date, '%Y%m%d')
            sym = rec[1]
            if uncompress:
                fname = '%s.csv' % (self.encode_symbol(sym))
            else:
                fname = '%s.csv.gz' % (self.encode_symbol(sym))
            
            bucket, key = self._build_bucket_and_key(date, sym, service)
            if service['file_structure'] == 0: # equities
                # equities file structure: year/date/X/XXX.csv.gz
                fpath = store_format % {'symbol': self.encode_symbol(sym), 'path': store_path, 'year': str(tdate.year), 'date': tdate.strftime('%Y%m%d'), 'base': sym[0], 'file': fname}
            elif service['file_structure'] == 1 or service['file_structure'] == 2: # futures
                # futures file structure: year/date/base/sym.csv.gz
                fpath = store_format % {'symbol': self.encode_symbol(sym), 'path': store_path, 'year': str(tdate.year), 'date': tdate.strftime('%Y%m%d'), 'base': sym[0:-2], 'file': fname}
            elif service['file_structure'] == 3: # options
                # futures file structure: year/date/base/sym.csv.gz
                sym_parts = self.encode_symbol(sym).split('!')
                fpath = store_format % {'symbol': self.encode_symbol(sym), 'path': store_path, 'year': str(tdate.year), 'date': tdate.strftime('%Y%m%d'), 'base': sym_parts[0], 'file': fname}
            else:
                raise Exception('Unknown service file structure')
            fdir = os.path.dirname(fpath)
            if not os.path.isdir(fdir):
                os.makedirs(fdir)
            task = {'access_key': self.access_key, 'secret_key': self.secret_key, 'profile_name': self.profile_name, 'bucket': bucket, 'key': key, 'fpath': fpath, 'uncompress': uncompress, 'debug': self.debug}
            tasks.append(task)
            result.append(fpath)
        res_tasks = download_async(num_threads, tasks)
        return [task['fpath'] for task in res_tasks if task['exists']]
    
    def download_list_bases(self, records, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of date-future_base pair
        :param records: list of date-future_base tuples
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        new_records = []
        for record in records:
            date, base = record
            date = self.__convert_date(date)
            symbols = self.get_futures_by_base(date, base, service)
            for symbol in symbols:
                new_records.append((date, symbol))
        if not new_records:
            return []
        return self.download_list(new_records, store_path, num_threads, uncompress, store_format, service)
    
    def download_symbols(self, dates, symbols, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of dates and symbols
        :param dates: list of dates
        :param symbols: list of symbols
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        service = self.__validate_service(service)
        all_dates = self.list_all_trade_dates(service)
        datesl = []
        for date in all_dates:
            if self.__convert_date(date) in dates:
                datesl.append(self.__convert_date(date))
        if not datesl:
            return []
        records = []
        for date in datesl:
            if '*' in symbols:
                symbols1 = self.get_symbols(date, service)
            else:
                symbols1 = symbols
            for sym in symbols1:
                records.append((date, sym))
        return self.download_list(records, store_path, num_threads, uncompress, store_format, service)
    
    def download_bases(self, dates, bases, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of dates and base futures
        :param dates: list of dates
        :param symbols: list of symbols
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        service = self.__validate_service(service)
        all_dates = self.list_all_trade_dates(service)
        datesl = []
        for date in all_dates:
            if self.__convert_date(date) in dates:
                datesl.append(self.__convert_date(date))
        if not datesl:
            return []
        records = []
        for date in datesl:
            index = self.get_symbols_index(date, service)
            for base in bases:
                symbols = self.get_futures_by_base_index(index, base)
                for sym in symbols:
                    records.append((date, sym))
        if not records:
            return []
        return self.download_list(records, store_path, num_threads, uncompress, store_format, service)
    
    def download_range_symbols(self, start_date, end_date, symbols, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of symbols and date range
        :param start_date: beginning date
        :param end_date: ending date
        :param symbols: list of symbols
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        start_date = self.__convert_date(start_date)
        end_date = self.__convert_date(end_date)
        service = self.__validate_service(service)
        dates = self.list_range_trade_dates(start_date, end_date)
        return self.download_symbols(dates, symbols, store_path, num_threads, uncompress, store_format, service)
    
    def download_range_bases(self, start_date, end_date, bases, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download files using list of base futures and date range
        :param start_date: beginning date
        :param end_date: ending date
        :param symbols: list of base futures
        :param store_path: directory to store data
        :param num_threads: number of threads (use 2 or more for concurrent download). default is 1
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        start_date = self.__convert_date(start_date)
        end_date = self.__convert_date(end_date)
        service = self.__validate_service(service)
        all_dates = self.list_all_trade_dates(service)
        records = []
        for date in all_dates:
            if ((start_date is None) or (date >= start_date)) and ((end_date is None) or (date <= end_date)):
                index = self.get_symbols_index(date, service)
                for base in bases:
                    symbols = self.get_futures_by_base_index(index, base)
                    for symbol in symbols:
                        records.append((date, symbol))
        return self.download_list(records, store_path, num_threads, uncompress, store_format, service)
    
    def download_single_symbol(self, date, symbol, store_path, uncompress=False, store_format=None, service=None):
        """
        Download single symbol for given date
        :param date: single date
        :param symbol: single symbol
        :param store_path: directory to store data
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: file name or None if doesn't exist
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        res = self.download_symbols([date], [symbol], store_path, 1, uncompress, store_format, service)
        return res[0] if res else None

    def download_single_base(self, date, base, store_path, num_threads=1, uncompress=False, store_format=None, service=None):
        """
        Download all symbols for base future and given date
        :param date: single date
        :param base: base future
        :param store_path: directory to store data
        :param uncompress: uncompress downloaded data if set to True. default is False
        :param store_format: file format mask. default is %(path)s/%(year)s/%(date)s/%(base)s/%(file)s
        :param service: quantgo service (from qgservice.py)
        :return: list of file names downloaded
        """
        date = self.__convert_date(date)
        service = self.__validate_service(service)
        futures = self.get_futures_by_base(date, base, service)
        if not futures:
            return []
        return self.download_symbols([date], futures, store_path, num_threads, uncompress, store_format, service)

    def __convert_date(self, date):
        if date is None:
            return None
        # make sure date is in correct format
        date = datetime.strptime(str(date), '%Y%m%d')
        return date.strftime('%Y%m%d')
