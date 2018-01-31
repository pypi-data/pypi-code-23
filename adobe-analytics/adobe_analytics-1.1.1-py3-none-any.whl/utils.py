import pandas as pd


def download_async(client, report_definition, suite_ids=None):
    """ Download a report definition for all suites asynchronously.
    :param client: Client
    :param report_definition: ReportDefinition
    :param suite_ids: list of str. Ideally sort your suites by expected size of response (smallest to largest).
    :return: DataFrame
    """
    suites = client.suites()
    suite_ids = suite_ids or suites.keys()

    print("queuing reports...")
    report_ids = _queue_reports(suite_ids, suites, report_definition)

    print("downloading reports...")
    dfs = _download_reports(suite_ids, suites, report_ids)
    return pd.concat(dfs)


def _queue_reports(suite_ids, suites, report_definition):
    """ Queue reports per reporting suite
    :param suite_ids: list of str
    :param suites: dict of Suite
    :param report_definition: ReportDefinition
    :return: dict, suite_id -> report_id
    """
    report_ids = dict()
    for suite_id in suite_ids:
        print(suite_id)
        suite = suites[suite_id]

        report_id = suite.queue(report_definition)
        report_ids[suite_id] = report_id
    return report_ids


def _download_reports(suite_ids, suites, report_ids):
    """ Download the queued reports
    :param suite_ids: list of str
    :param suites: dict of Suite
    :param report_ids: dict, suite_id -> report_id
    :return: list of DataFrame
    """
    dfs = list()
    for suite_id in suite_ids:
        print(suite_id)
        suite = suites[suite_id]
        report_id = report_ids[suite_id]

        df = suite.download(report_id)
        dfs.append(df)
    return dfs
