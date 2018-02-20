from i18n_base import get_files_in_dir_with_subdirs, ignore_files, iterate_items, convert_to_unicode, save_dict_to_JSON, convert_dir_path
import pandas as pd
import re
import requests
import json
import logging
import os
from pandas import compat

log = logging.getLogger('qordoba')

KEY_COUNT = 0
"""
1. test with subdirs etc. ob das get_files_in_dir_with_subdirs wirklich functioniert auf allen ebenen
2. in index_lookup. instead of == could say 99%match. e.g. "Ruby is fun." vs "Ruby is fun"
"""

i18n_PAIRS = dict()

def generate_new_key(value):
    global KEY_COUNT
    KEY_COUNT += 1
    r = requests.post('https://us-central1-qordoba-devel.cloudfunctions.net/keys-extractor', data={'text': value})
    try:
        key = r.text
    except ValueError:
        generate_new_key(value)

    if not key.split("_")[-1]:
        word_list = re.findall(r"[\w']+", value)
        bi_word = sorted(word_list, key=lambda x: len(x))[-2:]
        key_end = "_".join(bi_word)
        key = key + key_end
    return key


def strip_qoutes(string):
    if string[:1] == "'" and string[-1] == "'" or string[:1] == '"' and string[-1] == '"':
        string = string[1:-1].strip()
        string = strip_qoutes(string)
    return string


def get_all_key_values(json_dictionary, path, c):
    """"iteratsed through (nested) dict and gives back joined keys (joined with .) and their values
    input should be json_dictionary,empty list(), empty dict()
    """
    for key, value in iterate_items(json_dictionary):

        path.append(key)
        if type(value) is not dict:
            s_path = '.'.join(path)
            c[s_path] = value
        else:
            get_all_key_values(value, path, c)
        path.pop()

    return c


def get_json_dictionary(file):
    if 'json' in file[-4:]:
        data = open(file, "r").read()
        try:
            json_data = json.loads(data)
            return json_data
        except ValueError:
            log.info("ValueError, expected a valid JSON file for exitsing i18n file {}".format(file))
            return None


def accumulate_existing_i18n_key_value_pairs_from_all_files(i18n_file_list):
    """Getting key values from json or nested json dict
    i18n_file_list can be [file] or [[file][file]], depndent on subdirs in `existing_i18nfiles`"""

    # print("i18n_file_list: {}".format(i18n_file_list))
    sum_of_keys_values_from_i18n_files = dict()
    if any(isinstance(el, list) for el in i18n_file_list):  # if file ist file list
        i18n_file_list = [j for i in i18n_file_list for j in i]
    for file in i18n_file_list:
        print("FILE: {}".format(file))
        # this is important due to subdirs
        log.info('Reading in existing i18n-file `{}`.'.format(file))

        # if json content is not valid
        dictionary = get_json_dictionary(file)
        if not dictionary:
            sum_of_keys_values_from_i18n_files[file] = None

        key_value_pairs = get_all_key_values(dictionary, list(), dict())
        key_value_pairs = convert_to_unicode(key_value_pairs)
        sum_of_keys_values_from_i18n_files[file] = key_value_pairs

    # return self.convert(sum_of_keys_values_from_i18n_files)
    return sum_of_keys_values_from_i18n_files


def index_lookup(stringLiteral, localization_k_v):
    # checks if stringLiteral exists in values, gives back corresponding key or None
    for i18n_file in localization_k_v:
        if not localization_k_v[i18n_file]:
            continue
        for key, value in localization_k_v[i18n_file].items():
            if value.strip() == stringLiteral.strip():
                return key, i18n_file
            if key.strip() == stringLiteral.strip():
                return key, i18n_file
    return None, None


def add_existing_i18n_keys_to_df(i18n_file_list, df):
    """Reading in list of i18n-filepaths and current df.
    Giving out the new df with existing keys added."""

    log.info(" ... searching for existing keys.")
    # accumulate all key-values-pairs from the i18n-file
    existing_i18n_key_value_pairs = accumulate_existing_i18n_key_value_pairs_from_all_files(i18n_file_list)

    for column in df:
        for i in range(len(df.index)):
            # stripping quotes from start and end of string
            try:
                if index_lookup(df[column][i]["value"], existing_i18n_key_value_pairs) == (None, None):
                    continue
                else:
                    key, i18n_file = index_lookup(df[column][i]["value"], existing_i18n_key_value_pairs)
                    df[column][i]["existing_key"] = {"key": key, "i18n_file": i18n_file}
            except TypeError:
                continue
        # df['existing_keys'], df['existing_localization_file'] = izip(*df.iloc[:, -1].apply(lambda x: self.index_lookup(x, localization_k_v)))
    return df


def generate(_curdir, report_dir=None, export_dir=None, existing_i18nfiles=None):
    """ Given localization files exists, gives back existing keys.
    Further, generating new keys for values
    """
    report_files = get_files_in_dir_with_subdirs(report_dir)
    # ignoring file such as .git .DS_Store
    report_files = ignore_files(report_files)
    if not report_files:
        log.info("Seems like you have no reports in your directory {}".format(report_dir))

    for single_report_path in report_files:
        """Validate report"""
        if not single_report_path.endswith(('.json',)):
            log.info("Skipping file `{}`. Not a valid qordoba json report.".format(single_report_path))
            continue

        log.info("\b")
        log.info("Reading report {}".format(single_report_path))
        log.info("  " + u"\U0001F4E1" + "  " + " .. loading keys from outer space.\n (This could Take some time) \n\n ")
        log.info("\b")

        df = pd.read_json(single_report_path)

        """If i18n files already exists and user defines the path. will add existing keys to df"""
        if existing_i18nfiles:
            # retrieving the files from user given directory path
            i18n_files = get_files_in_dir_with_subdirs(existing_i18nfiles)
            i18n_files = ignore_files(i18n_files)
            # checking if valid i18n file (currently only supporting json)
            i18n_file_list = []
            for loc_file in i18n_files:
                if loc_file.endswith('json'):
                    i18n_file_list.append(loc_file)
                else:
                    log.info("Skipping file `{}`. Not a valid exitsting i18n-file. Has to be JSON.".format(loc_file))

            df = add_existing_i18n_keys_to_df(i18n_file_list, df)

        """Generating new keys by post (parameter: text=stringliteral) 
            reponse 200 are 5 keywords based on stringliteral"""
        df = pd.read_json(single_report_path)
        for column in df:
            for i in range(len(df.index)):
                try:
                    # stripping quotes from start and end of string
                    value_stripped = strip_qoutes(df[column][i]["value"])

                    # make sure key is not duplicated
                    key = i18n_PAIRS.get(value_stripped)
                    if not key:
                        key = generate_new_key(value_stripped)
                        i18n_PAIRS[value_stripped] = key

                    df[column][i]["generated_key"] = {"key": key}
                except TypeError:
                    continue
                if KEY_COUNT % 20 == 0:
                    log.info("{} keys created ".format(KEY_COUNT))

        log.info("\nProcess completed. " + u"\U0001F680" + u"\U0001F4A5")
        log.info("old report replaced by new report with keys")

        # replace report
        if not export_dir:
            os.remove(single_report_path)

            def to_dict_dropna(data):
                return dict((k, v.dropna().to_dict()) for k, v in compat.iteritems(data))

            data = to_dict_dropna(df)
            # data = df.to_dict()
            save_dict_to_JSON(single_report_path, data)
        else:
            def to_dict_dropna(data):
                return dict((k, v.dropna().to_dict()) for k, v in compat.iteritems(data))

            new_filename = "key-" + single_report_path.split("/")[-1]
            export_dir = convert_dir_path(export_dir)
            new_filepath = export_dir + new_filename
            data = to_dict_dropna(df)
            log.info("Saving report in export directory `{}`".format(new_filepath))
            # data = df.to_dict()
            save_dict_to_JSON(new_filepath, data)
            os.remove(single_report_path)