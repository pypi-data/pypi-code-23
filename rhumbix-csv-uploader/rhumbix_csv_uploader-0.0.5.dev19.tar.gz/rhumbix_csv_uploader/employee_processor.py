import requests
import logging
from rhumbix_csv_uploader.processor_utils import read_csv, parse_arguments, get_headers


logging.basicConfig(level=logging.INFO)
fieldnames = ["company_supplied_id", "first_name", "last_name", "classification-role",
              "trade", "is_active", "phone", "email"]
company_key = None
api_key = None
api_url = None
PROCESSOR_NAME = "employee_processor"


def read_employee_csv(path):
    return read_csv(path, fieldnames)


def transform_values(data):
    """
    Transforms the csv values into the Rhumbix API format
    is_active.Active => is_active.True etc.
    """
    for person in data:
        person['is_active'] = person['is_active'] == 'Active'
        person['classification'] = person['classification-role'].split('-')[0]
        person['user_role'] = person['classification-role'].split('-')[1]
        del person['classification-role']

    return data


def post_data(data):
    url = "https://async-{}/V1_0_1/{}/batch/employee/import".format(
        api_url, company_key)
    result = requests.post(url, headers=get_headers(api_key, PROCESSOR_NAME), json=data)
    return result


def get_batch_status(batch_id):
    url = 'https://async-{}/V1_0_1/{}/batch/employee/import/{}/status'.format(
        api_url, company_key, batch_id)
    return requests.get(url, headers=get_headers(api_key, PROCESSOR_NAME))


def process_csv(path, _company_key, _api_key, _api_url):
    global company_key
    global api_key
    global api_url
    company_key = _company_key
    api_key = _api_key
    api_url = _api_url
    data = read_employee_csv(path)
    data = transform_values(data)
    return post_data(data)


if __name__ == "__main__":
    args = parse_arguments()
    result = process_csv(args.csv_path, args.company_key, args.api_key, args.api_url)
    log_function = logging.info if 200 <= result.status_code <= 299 else logging.warning
    if log_function is logging.warning:
        log_function("Something went wrong with uploading csv data")
    log_function(result.status_code)
    log_function(result.json())
