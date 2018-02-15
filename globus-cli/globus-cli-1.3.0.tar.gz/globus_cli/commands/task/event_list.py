import click
import json

from globus_cli.parsing import common_options, task_id_arg
from globus_cli.safeio import formatted_print

from globus_cli.services.transfer import iterable_response_to_dict, get_client


@click.command('event-list', help='List Events for a given task')
@common_options
@task_id_arg
@click.option(
    "--limit", default=10, show_default=True, help="Limit number of results.")
@click.option(
    "--filter-errors", is_flag=True, help="Filter results to errors")
@click.option(
    "--filter-non-errors", is_flag=True, help="Filter results to non errors")
def task_event_list(task_id, limit, filter_errors, filter_non_errors):
    """
    Executor for `globus task-event-list`
    """
    client = get_client()

    # cannot filter by both errors and non errors
    if filter_errors and filter_non_errors:
        raise click.UsageError("Cannot filter by both errors and non errors")

    elif filter_errors:
        filter_string = "is_error:1"

    elif filter_non_errors:
        filter_string = "is_error:0"

    else:
        filter_string = ""

    event_iterator = client.task_event_list(
        task_id, num_results=limit, filter=filter_string)

    def squashed_json_details(x):
        is_json = False
        try:
            loaded = json.loads(x['details'])
            is_json = True
        except ValueError:
            loaded = x['details']

        if is_json:
            return json.dumps(loaded, separators=(',', ':'))
        else:
            return loaded.replace('\n', '\\n')

    formatted_print(event_iterator,
                    fields=(('Time', 'time'), ('Code', 'code'),
                            ('Is Error', 'is_error'),
                            ('Details', squashed_json_details)),
                    json_converter=iterable_response_to_dict)
