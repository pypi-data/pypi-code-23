import csv
import argparse
import json
import pkg_resources


def read_csv(path, fieldnames):
    data = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row in reader:
            data.append(row)
    return data


def get_headers(api_key, processor_name):
    return {
        'x-api-key': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Processor-Name': processor_name,
        'Processor-Version': pkg_resources.get_distribution("rhumbix_csv_uploader").version
    }


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument('company_key', nargs='?')
    parser.add_argument('api_key', nargs='?')
    args = parser.parse_args()
    if args.company_key is None or args.api_key is None:
        config_dict = json.load(open('config.json'))
        args.company_key = config_dict["company_key"]
        args.api_key = config_dict["api_key"]
    return args
