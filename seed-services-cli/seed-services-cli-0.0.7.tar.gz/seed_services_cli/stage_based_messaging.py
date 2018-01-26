import click
import csv
import json
import sys

from seed_services_client.stage_based_messaging import StageBasedMessagingApiClient  # noqa
from demands import HTTPServiceError


if sys.version_info.major == 2:
    file_open_mode = 'rb'
else:
    file_open_mode = 'r'


def get_api_client(url, token):
    return StageBasedMessagingApiClient(
        api_url=url,
        auth_token=token
    )


@click.pass_context
def schedules(ctx):
    """ List all schedules
    """
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    click.echo("Getting schedules")
    results = list(api.get_schedules()['results'])
    click.echo("Found %s results:" % len(results))
    for result in results:
        click.echo("%s: %s %s %s %s %s (m/h/d/dM/MY)" % (
                   result["id"], result["minute"], result["hour"],
                   result["day_of_week"], result["day_of_month"],
                   result["month_of_year"]))


@click.pass_context
def messagesets(ctx):
    """ List all messagesets
    """
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    click.echo("Getting messagesets")
    results = list(api.get_messagesets()['results'])
    click.echo("Found %s results (id, short_name, content_type, next_set,"
               " default_schedule, notes):" % len(results))
    for result in results:
        click.echo("%s,%s,%s,%s,%s,%s" % (
                   result["id"], result["short_name"], result["content_type"],
                   result["next_set"], result["default_schedule"],
                   result["notes"]))


@click.option('--message', '-m', type=click.INT,
              help='Filter by Message')
@click.option('--messageset', '-ms', type=click.INT,
              help='Filter by Messageset')
@click.option('--lang', '-l', type=click.STRING, help='Filter by language')
@click.option('--seqno', '-s', type=click.INT,
              help='Filter by sequence number')
@click.pass_context
def messages(ctx, message, messageset, lang, seqno):
    """ List all messages
    """
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    click.echo("Getting messages")
    params = {}
    if message:
        # get a very particular message
        try:
            results = [api.get_message(message_id=message)]
        except HTTPServiceError:
            click.echo("Message not found")
            ctx.abort()
    else:
        # use the filters
        if messageset:
            params["messageset"] = messageset
        if lang:
            params["lang"] = lang
        if seqno:
            params["sequence_number"] = seqno
        results = list(api.get_messages(params=params)['results'])
    click.echo("Found %s results (id, messageset, sequence_number, lang,"
               " text_content, binary_content):" % len(results))
    for result in results:
        click.echo("%s,%s,%s,%s,\"%s\",%s" % (
                   result["id"], result["messageset"],
                   result["sequence_number"],
                   result["lang"], result["text_content"],
                   result["binary_content"]))


@click.option('--message', '-m', type=click.INT,
              help='Filter by Message')
@click.option('--messageset', '-ms', type=click.INT,
              help='Filter by Messageset')
@click.option('--lang', '-l', type=click.STRING, help='Filter by language')
@click.option('--seqno', '-s', type=click.INT,
              help='Filter by sequence number')
@click.confirmation_option(help='Are you sure you want to drop the messages?')
@click.pass_context
def messages_delete(ctx, message, messageset, lang, seqno):
    """ Delete all messages matching filter
    """
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    click.echo("Getting messages to delete")
    params = {}
    if message:
        # get a very particular message
        try:
            results = [api.get_message(message_id=message)]
        except HTTPServiceError:
            click.echo("Message not found")
            ctx.abort()
    else:
        # use the filters
        if messageset:
            params["messageset"] = messageset
        if lang:
            params["lang"] = lang
        if seqno:
            params["sequence_number"] = seqno
        results = list(api.get_messages(params=params)['results'])
    click.echo("Found %s result(s)" % len(results))
    for result in results:
        if result["binary_content"]:
            api.delete_binarycontent(binarycontent_id=result["binary_content"])
            click.echo("Deleted binary file <%s>" % result["binary_content"])
            click.echo("Deleted message <%s>" % result["id"])
        else:
            api.delete_message(message_id=result["id"])


@click.option(
    '--csv', type=click.File(file_open_mode),
    help=('CSV file with columns for the endpoint'))
@click.option(
    '--json', type=click.File(file_open_mode),
    help=('JSON objects, one per line for the endpoint'))
@click.pass_context
def messages_import(ctx, csv, json):
    """ Import to the Stage Based Messaging service.
        binary_content fields should refer to filename in the current folder
    """
    if not any((csv, json)):
        raise click.UsageError("Please specify either --csv or --json.")
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    if csv:
        for msg in messages_from_csv(csv):
            if msg["binary_content"] is not None and \
                    msg["binary_content"] != "":
                msg = create_binarycontent(api, msg)
            click.echo("Importing message to messageset %(messageset)s." % msg)
            api.create_message(msg)
    if json:
        for msg in messages_from_json(json):
            if msg["binary_content"] is not None and \
                    msg["binary_content"] != "":
                msg = create_binarycontent(api, msg)
            click.echo("Importing message to messageset %(messageset)s." % msg)
            api.create_message(msg)


@click.option(
    '--csv', type=click.File(file_open_mode),
    help=('CSV file with columns for the endpoint'))
@click.option(
    '--json', type=click.File(file_open_mode),
    help=('JSON objects, one per line for the endpoint'))
@click.pass_context
def messages_update(ctx, csv, json):
    """ Update messages in the Stage Based Messaging service.
        binary_content fields should refer to filename in the current folder
    """
    if not any((csv, json)):
        raise click.UsageError("Please specify either --csv or --json.")
    api = get_api_client(ctx.obj.stage_based_messaging.api_url,
                         ctx.obj.stage_based_messaging.token)
    if csv:
        messages = messages_from_csv(csv)
    elif json:
        messages = messages_from_json(json)

    update_msgs = {}
    for message in messages:
        params = {}
        params["messageset"] = message["messageset"]
        params["lang"] = message["lang"]
        params["sequence_number"] = message["sequence_number"]
        results = list(api.get_messages(params=params)['results'])

        number_of_messages = len(results)
        if number_of_messages == 1:
            update_msgs[results[0]["id"]] = message
        elif number_of_messages > 1:
            raise click.UsageError("Multiple messages found.")
        elif number_of_messages < 1:
            raise click.UsageError("Message not found.")

    for msg_id, message in update_msgs.items():
        if message["binary_content"] is not None and \
                message["binary_content"] != "":
            message = create_binarycontent(api, message)
        click.echo("Updating message to messageset %(messageset)s." %
                   message)
        api.update_message(msg_id, message)


def create_binarycontent(api, msg):
    """ Create a binary content item and set the foreign key to new ID
    """
    click.echo("Uploading binary file %(binary_content)s." % msg)
    files = {'content': click.open_file(msg["binary_content"])}
    binary_content = api.create_binarycontent(files)
    # update the ref to a foreign key now
    msg["binary_content"] = binary_content["id"]
    return msg


def messages_from_csv(csv_file):
    reader = csv.DictReader(csv_file)
    if not (set(["messageset", "sequence_number", "lang", "text_content",
                 "binary_content"]) <= set(reader.fieldnames)):
        raise click.UsageError(
            "CSV file must contain messageset, sequence_number, lang,"
            " text_content, binary_content column headers.")
    for data in reader:
        yield {
            "messageset": data["messageset"],
            "sequence_number": data["sequence_number"],
            "lang": data["lang"],
            "text_content": data.get("text_content"),
            "binary_content": data.get("binary_content")
        }


def messages_from_json(json_file):
    for line in json_file:
        data = json.loads(line.rstrip("\n"))
        if not isinstance(data, dict) or not (
                set(["messageset", "sequence_number", "lang", "text_content",
                     "binary_content"]) <= set(data.keys())):
            raise click.UsageError(
                "JSON file lines must be objects containing messageset,"
                "sequence_number, lang, text_content, binary_content keys.")
        yield {
            "messageset": data["messageset"],
            "sequence_number": data["sequence_number"],
            "lang": data["lang"],
            "text_content": data.get("text_content"),
            "binary_content": data.get("binary_content")
        }
