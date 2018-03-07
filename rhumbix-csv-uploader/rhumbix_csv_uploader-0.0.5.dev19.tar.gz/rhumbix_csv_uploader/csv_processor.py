import argparse
import json
import glob
import logging
import time
import os
from os.path import dirname, abspath
import rhumbix_csv_uploader.employee_processor as employee_processor
import rhumbix_csv_uploader.project_processor as project_processor
import rhumbix_csv_uploader.cost_code_processor as cost_code_processor


employee_filename_pattern = "rhumbix_employee*.csv"
project_filename_pattern = "rhumbix_project*.csv"
cost_code_filename_pattern = "rhumbix_cost_code*.csv"
DEFAULT_API_URL = "api.rhumbix.com"
BATCH_LOOKUP_CYCLE_DELAY_SECONDS = 2
TWO_WEEKS_IN_SECONDS = 2 * 7 * 24 * 60 * 60


def clean_processed_folder(base_path):
    logging.info("Cleaning processed directory of expired files")
    processed_path = os.path.join(base_path, "processed")
    processed_path = os.path.join(processed_path, '')
    if not os.path.exists(processed_path):
        return
    paths = glob.glob("%s%s" % (processed_path, "*.csv"))
    for path in paths:
        if time.time() - os.path.getmtime(path) > TWO_WEEKS_IN_SECONDS:
            logging.info("Removing %s as it has expired", path)
            os.remove(path)


def move_file_to_processed(path):
    if os.path.exists(path):
        parent_path = (dirname(abspath(path)))
        processed_path = os.path.join(parent_path, "processed")
        if not os.path.exists(processed_path):
            # Create the processed directory
            os.makedirs(processed_path)
        processed_path = os.path.join(processed_path, os.path.basename(path))
        if os.path.exists(processed_path):
            logging.warning("Overwriting %s in processed directory!" % processed_path)
        os.rename(path, processed_path)
    else:
        logging.warning("move_file_to_processed received nonexistent file: %s" % path)


def main():
    global employee_filename_pattern
    global project_filename_pattern
    global cost_code_filename_pattern
    parser = argparse.ArgumentParser()
    parser.add_argument("csvs_directory")
    parser.add_argument('company_key', nargs='?')
    parser.add_argument('api_key', nargs='?')
    parser.add_argument('api_url', nargs='?')
    args = parser.parse_args()

    config_dict = None
    if os.path.exists('config.json'):
        config_dict = json.load(open('config.json'))
        for name in ["company_key", "api_key", "api_url"]:
            if not getattr(args, name, None):
                setattr(args, name, config_dict.get(name, None))

    for name in ["company_key", "api_key"]:
        if not getattr(args, name, None):
            logging.error("{} is not set. It can be passed as a command line argument or in config.json".format(name))

    if args.api_url is None:
        args.api_url = DEFAULT_API_URL

    # Load custom file name patterns
    if config_dict is not None:
        if "employee_filename_pattern" in config_dict:
            employee_filename_pattern = config_dict["employee_filename_pattern"]
        if "project_filename_pattern" in config_dict:
            project_filename_pattern = config_dict["project_filename_pattern"]
        if "cost_code_filename_pattern" in config_dict:
            cost_code_filename_pattern = config_dict["cost_code_filename_pattern"]

    args.csvs_directory = os.path.join(args.csvs_directory, '')

    logging.info("Processing directory %s with company_key=%s and api_key=%s and api_url=%s" %
        (args.csvs_directory, args.company_key, args.api_key, args.api_url))

    clean_processed_folder(args.csvs_directory)

    employee_paths = glob.glob("%s%s" % (args.csvs_directory, employee_filename_pattern))
    logging.info("Employee files=%s" % employee_paths)

    project_paths = glob.glob("%s%s" % (args.csvs_directory, project_filename_pattern))
    logging.info("Project files=%s" % project_paths)

    cost_code_paths = glob.glob("%s%s" % (args.csvs_directory, cost_code_filename_pattern))
    logging.info("Cost Code Files=%s" % cost_code_paths)

    employee_batches = []
    for path in employee_paths:
        logging.info("Processing employee file: %s" % path)

        result = employee_processor.process_csv(path, args.company_key, args.api_key, args.api_url)
        if 'batch_key' not in result.json():
            logging.error("Request failed! Here is the body:\n%s" % result.json())
            continue

        batch_key = result.json()["batch_key"]
        logging.info("Finished file:%s with batch id: %s" % (path, batch_key))
        employee_batches.append({"path": path, "batch_key": batch_key})

    project_batches = []
    for path in project_paths:
        logging.info("Proccessing project file: %s" % path)

        result = project_processor.process_csv(path, args.company_key, args.api_key, args.api_url)
        if 'batch_key' not in result.json():
            logging.error("Request failed! Here is the body:\n%s" % result.json())
            continue

        batch_key = result.json()["batch_key"]
        logging.info("Finished file:%s with batch id: %s" % (path, batch_key))
        project_batches.append({"path": path, "batch_key": batch_key})

    cost_code_batches = []
    for path in cost_code_paths:
        logging.info("Processing cost code file: %s" % path)

        result = cost_code_processor.process_csv(path, args.company_key, args.api_key, args.api_url)
        if 'batch_key' not in result.json():
            logging.error("Request failed! Here is the body:\n%s" % result.json())
            continue

        batch_key = result.json()["batch_key"]
        logging.info("Finished file:%s with batch id: %s" % (path, batch_key))
        cost_code_batches.append({"path": path, "batch_key": batch_key})

    logging.info("All csv files uploaded. Monitoring batch status...")
    # Wait for all the batches to get done. The [:] makes a temporary copy as the list is mutated
    while len(employee_batches) + len(project_batches) + len(cost_code_batches) > 0:
        for batch in employee_batches[:]:
            batch_key = batch["batch_key"]
            result = employee_processor.get_batch_status(batch_key)
            body = result.json()
            logging.info("Batch id %s has status: %d %s" % (batch_key, result.status_code, body["status"]))
            if result.status_code == 200 and body["status"] == "COMPLETE":
                move_file_to_processed(batch["path"])
                employee_batches.remove(batch)

        for batch in project_batches[:]:
            batch_key = batch["batch_key"]
            result = project_processor.get_batch_status(batch_key)
            body = result.json()
            logging.info("Batch id %s has status: %d %s" % (batch_key, result.status_code, body["status"]))
            if result.status_code == 200 and body["status"] == "COMPLETE":
                move_file_to_processed(batch["path"])
                project_batches.remove(batch)

        for batch in cost_code_batches[:]:
            batch_key = batch["batch_key"]
            result = cost_code_processor.get_batch_status(batch_key)
            body = result.json()
            logging.info("Batch id %s has status: %d %s" % (batch_key, result.status_code, body["status"]))
            if result.status_code == 200 and body["status"] == "COMPLETE":
                move_file_to_processed(batch["path"])
                cost_code_batches.remove(batch)

        time.sleep(BATCH_LOOKUP_CYCLE_DELAY_SECONDS)

    logging.info("All batches have completed processing")


if __name__ == "__main__":
    main()
