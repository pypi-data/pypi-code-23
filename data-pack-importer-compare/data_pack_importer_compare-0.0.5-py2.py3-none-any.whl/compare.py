import argparse
import json
import os
import re
from datetime import datetime

import pandas as pd


class color:
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DPICException(Exception):
    """Package Base exception """
    def __init__(self, message):
        print("{}{}{}".format(color.RED, message, color.END))


class WbInfoException(DPICException):
    """Workbook info Exception"""


class SiteData(object):

    def __init__(self, country, level, typ, path):
        self.country = country
        self.level = level
        self.typ = typ
        self.path = path
        self.identifier = self.file_identifier()
        self.df = self.create_data_frame()
        self.info = self.get_info()
        self.validate_info()

    def create_data_frame(self):
        with open(self.path, 'r') as jf:
            data = json.dumps(sorted(json.load(jf).get('data')))
            return pd.read_json(data)

    def get_info(self):
        with open(self.path, 'r') as jf:
            return json.load(jf)['wb_info']

    def validate_info(self):
        exc = []
        if self.info.get('wb_path') in ("", None):
            exc.append("wb_path not existent")

        try:
            datetime.strptime(self.info.get('timestamp'), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            exc.append("datetime could not be parsed: {}".format(self.info.get('timestamp')))
            pass

        valid_wb_types = {'NORMAL', 'HTS', 'NORMAL_SITE', 'HTS_SITE'}
        if self.info.get('wb_type') not in valid_wb_types:
            exc.append("wb_type not {}: {}".format(valid_wb_types, self.info.get('wb_type')))
        if self.info.get('wb_type') != self.typ.upper():
            exc.append("wb_type not matching to argument {}: {}".format(self.info.get('wb_type'), self.typ))

        if self.info.get('ou_name') in ("", None):
            exc.append('ou_name not existent')

        if not re.compile('^[A-Za-z][A-Za-z0-9]{10}$').match(self.info.get('ou_uid')):
            exc.append('ou_uid not a valid DHIS2 uid: {}'.format(self.info.get('ou_uid')))

        if not isinstance(self.info.get('is_clustered'), bool):
            exc.append('is_clustered is not true or false')

        if self.info.get('distribution_method') not in (2017, 2018):
            exc.append('distribution_method not 2017 or 2018')

        if self.info.get('support_files_path') in ("", None):
            exc.append('support_files_path not existent')

        if exc:
            raise WbInfoException("{}:\n{}".format(self.path, "\n".join(exc)))

    def file_identifier(self):
        common = self.path
        for i in range(2):
            common = os.path.dirname(common)
        return os.path.relpath(self.path, common)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and pd.DataFrame.equals(self.df, other.df)

    def __ne__(self, other):
        return not self == other


def parse_args():
    parser = argparse.ArgumentParser(usage='%(prog)s',
                                     description="Compare data JSONs in folders")
    parser.add_argument('--folder1',
                        dest='folder1',
                        action='store',
                        required=True,
                        help="File path of first folder"
                        )

    parser.add_argument('--folder2',
                        dest='folder2',
                        action='store',
                        required=True,
                        help="File path of second folder"
                        )

    parser.add_argument('--country',
                        dest='country',
                        action='store',
                        required=True,
                        help="Country string"
                        )

    parser.add_argument('--level',
                        dest='level',
                        action='store',
                        required=True,
                        choices={'psnu', 'site'},
                        help="Level"
                        )

    parser.add_argument('--type',
                        dest='type',
                        action='store',
                        required=True,
                        choices={'normal', 'hts'},
                        help="Type"
                        )

    return parser.parse_args()


def get_path(directory, country, level, typ):
    return os.path.join(directory, '{}_{}_{}.json'.format(country, level, typ))


def detailed(sd1, sd2):
    df = sd1.df.merge(sd2.df, how='outer', indicator=True)
    with pd.option_context('display.max_rows', 30, 'display.max_columns', 8):
        print(df.copy().rename(columns={
            'attributeoptioncombo': 'aoc',
            'categoryoptioncombo': 'coc',
            'supportType': 'st'
        })[df['_merge'] != 'both'])
    now = datetime.now().strftime('%F-%H%M%S')
    filename = "{}_{}_{}_diff_{}.csv".format(
        sd1.country,
        sd1.level,
        sd1.typ,
        now
    )
    pd.DataFrame.to_csv(df, filename)
    print("Saved to {}{}{}".format(color.BOLD, filename, color.END))


def compare(sd1, sd2):
    equal = sd1 == sd2

    c = color.RED if not equal else color.BOLD
    f1 = "{}{}{}".format(c, sd1.file_identifier(), color.END)
    f2 = "{}{}{}".format(c, sd2.file_identifier(), color.END)
    eq = "{}{}{}".format(c, equal, color.END)

    print("Comparing {} with {} - equal: {}".format(f1, f2, eq))
    if not equal:
        detailed(sd1, sd2)


def run(dir_paths, country, level, typ):
    comparable_files = [get_path(f, country, level, typ) for f in dir_paths]

    sd1 = SiteData(country, level, typ, comparable_files[0])
    sd2 = SiteData(country, level, typ, comparable_files[1])
    compare(sd1, sd2)


def main():
    args = parse_args()
    run(
        dir_paths=[args.folder1, args.folder2],
        country=args.country,
        level=args.level,
        typ=args.type
    )


if __name__ == '__main__':
    main()
