#!/usr/bin/env python

import os
import re
import sys
import tempfile
from functools import wraps
from urllib.parse import urljoin
from collections import defaultdict

import arrow
import click
import editor
import yaml
from dotmap import DotMap
from jira.exceptions import JIRAError

from .tools import config_read, config_save
from .tools import print_table_from_dict, get_hour_min, check_file_present
from .tools import load_and_parse_any
from .tools import process_multiline_str
from .tools import CliError
from .parsehelpers import parse_date_str, parse_time_str
from .parsehelpers import parse_date_and_time_str
from .parsehelpers import process_template
from .jirahelpers import TICKET_CREATE_DEFAULT_TEMPLATE
from .jirahelpers import TICKET_CREATE_DEFAULT_VALUES
from .jirahelpers import create_dict_prep
from .jirahelpers import worklogs_get_latest_stop
from .jirahelpers import add_worklog
from .jirahelpers import check_for_alias
from .jirahelpers import create_dict_jira
from .jirahelpers import construct_jql_string_from_saved_searches
from .jirahelpers import get_jira
from .jirahelpers import get_ticket_object
from .jirahelpers import get_worklogs_for_date_and_user
from .jirahelpers import perform_search
from .jirahelpers import search_wrapper
from .workloghelpers import log_csv, log_yaml, calculate_logged_time_for


# ============================================================================
# VERSION
# ============================================================================


__version__ = "0.17.0"


# ============================================================================
# CLICK HELP PARAMETER
# ============================================================================


CLI_HELP = dict(help_option_names=['-h', '--help'])


# ============================================================================
# DECORATORS
# ============================================================================


def handle_errors(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except JIRAError as e:
            print("JIRA ERROR: {}".format(e.text))
            sys.exit(-1)
        except CliError as e:
            print("ERROR: {}".format(e.message))
            sys.exit(e.exitcode)
    return inner


# ============================================================================
# COMMANDS START HERE
# ============================================================================


@click.group()
def cli():
    pass


@cli.command(context_settings=CLI_HELP)
def version():
    """
    Print the version and exits.
    """
    print(__version__)


@cli.command(context_settings=CLI_HELP)
@click.option("--jira-url", prompt=True,
              default=lambda: os.environ.get("JIRA_URL", ''))
@click.option("--username", prompt=True,
              default=lambda: os.environ.get("JIRA_USER", ''))
@click.option("--password", prompt=True,
              hide_input=True,
              default=lambda: os.environ.get("JIRA_PASSWORD", ''))
@handle_errors
def init(**kwargs):
    """
    Needs to be called one time to initialize URL, user and password.
    """
    try:
        config = config_read()
        config.update(kwargs)
    except CliError as e:
        config = kwargs
    config_save(config)


@cli.command(context_settings=CLI_HELP)
@click.option("-v", "--verbose",
              is_flag=True,
              help="Print the final JQL search string used before searching")
@click.option("-l", "--limit",
              default=50,
              help="Limit number of results "
                   "(defaults to 50, 0 means retrieve all)")
@click.argument("search-aliases", nargs=-1, required=True)
@handle_errors
def lookup(verbose, limit, search_aliases):
    """
    Call a previously saved search.

    You can combine multiple defined aliasesto do things like this:

    $ jira lookup prj-in-progress due-1m

    Both search aliases (prj-in-progress and due-1m) must exist beforehand.
    If you execute this, the following search will be performed:

      ((prj-in-progress) AND (due-1m))

    ORDER BY CLAUSES

    Please make sure that AT MOST ONE QUERY contains an "ORDER BY" part. If
    any search does, the ORDER BY part of the query is extracted and moved
    at the end. If more than one ORDER clause exists the behavior is
    undefined. (It might work, it might not, it might order by random things).

    COMBINING SEARCHES USING JQL AND LOOKUP:

    \b
    $ jira jql --just-save  --save-as order-duedate  ORDER BY duedate
    $ jira jql --just-save  --save-as in-progress    "status = 'In Progress'"
    $ jira jql --just-save  --save-as mine           "assignee = currentUser()"
    $ jira lookup in-progress mine order-duedate
    [...]
    """
    config = config_read()
    saved_searches = config.get("saved_searches", {})
    use_queries = []
    if search_aliases[0] not in saved_searches:
        print("No such search alias: '{}'".format(search_aliases[0]))
        sys.exit(-1)
    use_queries.append(saved_searches[search_aliases[0]])
    for falias in search_aliases[1:]:
        if falias not in saved_searches:
            print("Search filter '{}' not defined.")
            sys.exit(-1)
        use_queries.append(saved_searches[falias])
    # now, sort that the ORDER BY thing is last

    jql_str = construct_jql_string_from_saved_searches(use_queries)
    if verbose:
        print("JQL search string: ", jql_str)
    perform_search(jql_str, limit=limit)


@cli.command(name="remove-search", context_settings=CLI_HELP)
@click.argument("search-alias")
@handle_errors
def remove_search(search_alias):
    """
    Remove a search alias.
    """
    config = config_read()
    if "saved_searches" not in config:
        print("No search aliases defined.")
        sys.exit(-1)
    if search_alias not in config["saved_searches"]:
        print("No such search alias: '{}'".format(search_alias))
        sys.exit(-1)
    del config["saved_searches"][search_alias]
    config_save(config)
    print("Saved search '{}' removed.".format(search_alias))


@cli.command(name="list-searches", context_settings=CLI_HELP)
@handle_errors
def list_searches():
    """
    List all saved searches.
    """
    config = config_read()
    if "saved_searches" not in config:
        print("No saved searches.")
        sys.exit(-1)
    print_table_from_dict(config["saved_searches"],
                          header=("alias", "search query"))


@cli.command(name="clear-searches", context_settings=CLI_HELP)
@handle_errors
def clear_searches():
    """
    Delete all saved searches.
    """
    config = config_read()
    if "saved_searches" not in config:
        print("No saved searches.")
        sys.exit(-1)
    del config["saved_searches"]
    config_save(config)
    print("All saved searches cleared.")


@cli.command(context_settings=CLI_HELP)
@click.argument("searchstring", nargs=-1)
@click.option("--save-as", default=None)
@click.option("--just-save", is_flag=True)
@click.option("-l", "--limit",
              default=50,
              help="Limit number of results "
                   "(defaults to 50, 0 means retrieve all)")
@handle_errors
def search(searchstring, save_as, just_save, limit):
    """
    Search for header or summary text.

    If you specify --save-as, the query is executed and - on success - saved
    as a search alias which you recall using the 'lookup' command later.

    If you additionally specify --just-save, the search is just saved as alias
    but not executed ('just saved', right? :).
    """
    query = " ".join(searchstring)
    query = "summary ~ \"{0}\" OR description ~\"{0}\"".format(query)
    search_wrapper(query, save_as, just_save=just_save, limit=limit)


@cli.command(context_settings=CLI_HELP)
@click.argument("jql_string", nargs=-1)
@click.option("-s", "--save-as", default=None,
              help="Save the search for future quick retrieval using 'lookup'")
@click.option("--just-save", is_flag=True,
              help="Don't actually perform the search, directly save it")
@click.option("-l", "--limit",
              default=50,
              help="Limit number of results "
                   "(defaults to 50, 0 means retrieve all)")
@handle_errors
def jql(jql_string, save_as, just_save, limit):
    """
    Search for tickets using JQL.

    If you specify --save-as, the query is executed and - on success - saved
    as a search alias which you recall using the 'lookup' command later.

    If you additionally specify --just-save, the search is just saved as alias
    but not executed ('just saved', right? :).
    """
    query = " ".join(jql_string)
    search_wrapper(query, save_as, just_save, limit=limit)


@cli.command(name="cleanup-day", context_settings=CLI_HELP)
@click.argument("date", default="today")
@click.option("--day-start", default="0900",
              help="When the first worklog should start. "
                   "Format must be HHMM.")
@handle_errors
def cleanup_day(date, day_start):
    """
    Arrange the worklogs nicely for a given day.

    This means that it will re-sort all the logged time entries to follow one
    after another, so that it looks nice in the JIRA calendar view.

    If DATE is omitted it defaults to 'today'.
    """
    start_time = parse_date_and_time_str(date, day_start)
    tickets_and_logs = get_worklogs_for_date_and_user(start_time)

    # returns [(ticket, worklog),...]
    # now sort by ticket key, then duration ;)
    def sortfunc(x): return x[0].key + "{:08d}".format(x[1].timeSpentSeconds)

    tickets_and_logs = sorted(tickets_and_logs, key=sortfunc)
    for ticket, wlog in tickets_and_logs:
        next_time = start_time.replace(seconds=+int(wlog.timeSpentSeconds))
        print("{:<5} - {:<5}:  {:<10}  {}".format(
            start_time.format("HH:mm"), next_time.format("HH:mm"),
            ticket.key,
            wlog.comment if hasattr(wlog, "comment") and wlog.comment
            else "<no comment given>"
        ))
        # don't do it if we already did this before ;)
        if not arrow.get(wlog.started) == start_time:
            wlog.update({'started': start_time.format("YYYY-MM-DDTHH:mm:ss.SSSZ")})
        start_time = next_time


@cli.command(name="log-work", context_settings=CLI_HELP)
@click.option("-d", "--date", default="today",
              metavar="DATESTR",
              help="Specify the date to log the work for, defaults to 'today'")
@click.option("-c", "--comment", default=None,
              help="Optional comment for the work log")
@click.option("-m", "--multiline", is_flag=True,
              help="Starts an editor for multiline comment entry.")
@click.option("--dry-run", is_flag=True,
              help="Don't actually log, just print the info")
@click.argument("ticket")
@click.argument("logged_work", nargs=-1)
@handle_errors
def log_work(date, comment, multiline, dry_run, ticket, logged_work):
    """
    Create a work log entry in a ticket.

    The simplest way of calling this command is:

        log_work   [OPTIONS]   TICKET_ID   WORKLOG_STRING(S)

    You can specify the DATE using several ways:

    \b
    * "m1", "m3", etc. means (m)inus 1 and (m)inus 3 days (yesterday and
      3 days ago).
    * 'today' is an alias for 'm0', which is (m)inos 0 days, which is today.
    * "1" and "14" means the 1st respectively the 14th of the current month.
    * "0110" is the 10th of January this year
    * "20150110" the 10th of January in the year 2015.

    NOTE:

    As of now all work logs will be created at 09:00h s

    EXAMPLES:

    \b
    log-work TK-1 2h 30m                (log "2h 30m" today on ticket TK-1)
    log-work -d today     TK-1 12h 30m  (same as above)
    log-work -d m0        TK-1 12h 30m  (same as above, m0 == today)
    log-work -d m1        TK-1 12h 30m  (same, just for YESTERDAY ("m1"))
    log-work -d 12        TK-1 1.5h 12  (same, just on the 12th of THIS MONTH)
    log-work -d 0112      TK-1 1.5h     (same, just for Jan 12th THIS YEAR)
    log-work -d 20160112  TK-1 1.5h     (same, just for Jan 12th, 2016)
    log-work -c "heyho!" -d m0 TK-1 2h  (you can figure this out ;)

    """
    # TODO: should append after latest worklog entry at the given date
    # TODO: should have a -f/--fill option to use last stop time until NOW
    # logdata must be: HOURS DATE START_TIME
    if comment and multiline:
        print("Cannot use -c and -m together.")
        sys.exit(-1)
    if multiline:
        start_content = b"# enter comments here. " \
                        b"lines starting with # are ignored."
        comment = str(editor.edit(contents=start_content), encoding="utf-8")
        comment = "\n".join(process_multiline_str(comment,
                                                  no_comments=True))
    worklog_string = " ".join(logged_work)
    worklog_date = parse_date_and_time_str(date, '0900')
    tickets_and_logs = get_worklogs_for_date_and_user(worklog_date)
    if len(tickets_and_logs):
        worklog_date = worklogs_get_latest_stop(tickets_and_logs)
    ticket = check_for_alias(ticket)
    # TODO - remove default timezone!!
    print("Logging {} for {} on {}"
          .format(worklog_string, ticket,
                  worklog_date.to('Europe/Berlin').format()))
    if dry_run:
        print("Stopping here. No log was performed.")
    else:
        add_worklog(ticket, worklog_date.datetime, worklog_string, comment)


@cli.command(name="log-time-file", context_settings=CLI_HELP)
@click.argument("file")
@click.option("-dl", "--delimiter", default=';',
              help="delimiter for csv file")
@handle_errors
def log_fromfile(file, delimiter):
    jira = get_jira()
    if '.csv' in file:
        log_csv(file, jira, delimiter)
    elif '.yaml' in file:
        log_yaml(file, jira)


@cli.command(context_settings=CLI_HELP)
@click.argument("ticket_id")
@click.argument("alias_name")
@click.option("--unsafe", is_flag=True,
              help="Don't try to check whether the ticket actually exists")
@handle_errors
def alias(ticket_id, alias_name, unsafe=False):
    """
    Create an alias name for a ticket.

    That alias can be used to log time on instead of the ticket name.
    """
    config = config_read()
    if not unsafe:
        jira = get_jira()
        jira.issue(ticket_id)
    if "aliases" not in config:
        config["aliases"] = {}
    config["aliases"][alias_name] = ticket_id
    config_save(config)
    print("Alias '{}' -> '{}' created successfully."
          .format(alias_name, ticket_id))


@cli.command(name="remove-alias", context_settings=CLI_HELP)
@click.argument("alias_name")
@handle_errors
def remove_alias(alias_name):
    """
    Remove a ticket alias.
    """
    config = config_read()
    if "aliases" not in config or alias_name not in config["aliases"]:
        print("No such alias: '{}'".format(alias_name))
    else:
        del config["aliases"][alias_name]
        config_save(config)
        print("Alias '{}' removed.".format(alias_name))


@cli.command(name="list-aliases", context_settings=CLI_HELP)
@handle_errors
def list_aliases():
    """
    List all ticket aliases.
    """
    config = config_read()
    if "aliases" not in config or len(config["aliases"]) == 0:
        print("No aliases defined.")
    else:
        print_table_from_dict(config["aliases"])


@cli.command(name="clear-aliases", context_settings=CLI_HELP)
@handle_errors
def clear_aliases():
    """
    Remove ALL ticket aliases.
    """
    config = config_read()
    if "aliases" not in config or len(config["aliases"]) == 0:
        print("No aliases defined.")
    else:
        del config["aliases"]
        config_save(config)
        print("All aliases cleared.")


@cli.command(name="fill-day", context_settings=CLI_HELP)
@click.option("-c", "--comment", default="fill day",
              help="Optional worklog comment, defaults to 'fill day'")
@click.option("--day-hours", default=8.0)
@click.option("--day-start", default="0900",
              metavar="TIMESTR",
              help="The start time of the day, format HHMM")
@click.option("-t", "--ticket", default=None,
              metavar="TICKET_ID",
              help="Specify the ticket, the ticket last used with --default "
                   "is used when omitted")
@click.option("-s", "--save",
              is_flag=True,
              help="Save the given ticket as the 'default' ticket for future "
                   "uses in case -t was not given")
@click.argument("date", default='today',
                metavar="DATESTR")
@handle_errors
def fill_day(comment, day_hours, day_start, ticket, save, date):
    """
    "Fill" a day up by adding a worklog so that the day has a certain number of
    hours logged on tickets.

    'ticket' can be a ticket ID, or any defined ticket alias. 'datestr'
    defaults to 'today' if omitted.

    EXAMPLES:

    Fill up today so we have 8 hours logged, use ticket TCK-1 for the logged
    time:

    $ fill-day -t TCK-1

    Fill up "yesterday" so we have 9 hours logged, and save ticket TCK-1 as the
    default ticket to be used for future invocations:

    $ fill-day -s -t TCK-2 --day-hours 9 m1

    Fill up today and use the default ticket for the added worklogs (you have
    to have called this with the -d flag to specify the default ticket at least
    once):

    $ fill-day
    """
    start_h, start_m = parse_time_str(day_start)
    start_time = parse_date_str(date).floor('day')\
                                     .replace(hour=start_h, minute=start_m)
    config = config_read()
    if "fill_day" not in config and not ticket:
        print("No default ticket specified. Please use -d flag once.")
        sys.exit(-1)
    if save and not ticket:
        print("Cannot use -s without -t.")
        sys.exit(-1)
    if ticket and save:
        # try to see if it exists so we don't save a bogus ticket id
        ticket_obj = get_ticket_object(ticket)
        config["fill_day"] = {'default_ticket': ticket_obj.key}
        config_save(config)
        print("Saved ticket {} as default ticket.".format(ticket_obj.key))
    # now we should be fine in all cases ;)
    if not ticket:
        ticket = config["fill_day"]["default_ticket"]

    # get the tickets
    tickets_and_logs = get_worklogs_for_date_and_user(start_time)

    # calculate logging data
    logged_work_secs = calculate_logged_time_for(tickets_and_logs)
    yet_to_log_secs = day_hours * 60 * 60 - logged_work_secs
    # sanity check
    if yet_to_log_secs < 60:
        print("You have already {}h {}m logged, not filling up."
              .format(*get_hour_min(logged_work_secs)))

    # get start time of new worklog
    use_start_time = start_time
    if len(tickets_and_logs) > 0:
        use_start_time = worklogs_get_latest_stop(tickets_and_logs)
        if use_start_time > start_time.ceil('day'):
            use_start_time = start_time

    # finally, log.
    log_string = "{}h {}m".format(*get_hour_min(yet_to_log_secs))
    print("{}: adding {} to {} (fill up day to {} hours)."
          .format(start_time.format("YYYY-MM-DD"),
                  log_string, ticket, day_hours))
    add_worklog(ticket, use_start_time, log_string, comment)


@cli.command(name="list-worklogs", context_settings=CLI_HELP)
@click.argument("date", default='today')
@handle_errors
def list_worklogs(date):
    """
    List all logs for a given day.

    See "jira log-work -h" for help about the date strings.
    """
    date_obj = parse_date_str(date)
    tickets_and_logs = get_worklogs_for_date_and_user(date_obj)
    logged_work_secs = calculate_logged_time_for(tickets_and_logs)
    # create a list like [(log_entry, ticket_obj), ...]
    tuples = [(v, sl[0]) for sl in tickets_and_logs for v in sl[1]]
    for log, ticket in sorted(tuples, key=lambda x: x[0].started):
        t_start = arrow.get(log.started).strftime("%H:%M")
        t_hrs, t_min = get_hour_min(log.timeSpentSeconds)
        cmt = log.comment \
            if hasattr(log, "comment") and log.comment \
            else "<no comment entered>"
        print("{:<8} {:<8} {:<8}  {:>2}h {:>2}m   {}"
              .format(log.id, ticket.key, t_start, t_hrs, t_min, cmt))
    print("\nSUM: {}h {}m"
          .format(logged_work_secs // 3600, (logged_work_secs % 3600) // 60))


@cli.command(name="list-work", context_settings=CLI_HELP)
@click.argument("date", default='today')
@handle_errors
def list_work(date):
    """
    List on which tickets you worked how long on a given day.

    See "jira log-work -h" for help about the date strings.
    """
    date_obj = parse_date_str(date)
    tickets_and_logs = get_worklogs_for_date_and_user(date_obj)

    # prepare calculation and data links
    collector = defaultdict(int)
    ticket_to_obj = {k.key: k for k, _ in tickets_and_logs}
    total_sum = 0

    # calculate the time spent on each ticket
    for k, v in tickets_and_logs:
        collector[k.key] += v.timeSpentSeconds
        total_sum += v.timeSpentSeconds

    # now output the result, sorted by duration
    for ticket, time_secs in sorted(collector.items(), key=lambda x: x[1]):
        use_time = "{:2}h {:2}m".format(*get_hour_min(time_secs))
        use_sum = ticket_to_obj[ticket].fields.summary
        print("{:<10} {:<8}  {}".format(ticket, use_time, use_sum))

    # print final sum
    print("\nSUM: {}h {}m".format(*get_hour_min(total_sum)))


@cli.command(name="delete-worklog", context_settings=CLI_HELP)
@click.argument("ticket-id")
@click.argument("worklog-id")
@handle_errors
def delete_worklog(ticket_id, worklog_id):
    """
    Delete a worklog entry by ID.

    Unfortunately you really need the ticket ID for the API it seems.
    """
    jira = get_jira()
    jira.worklog(check_for_alias(ticket_id), worklog_id).delete()


@cli.command(name="new", context_settings=CLI_HELP)
@click.option("-s", "--set", "field_values",
              multiple=True, metavar="FIELD=VAL",
              help="Set a field value manually. Takes precedence over "
                   "input data, even if you replace it in the template")
@click.option("--noi", is_flag=True,
              help="Non-interactive, will NOT open an editor. This is "
                   "intended for non-interactive, commandline only use.")
@handle_errors
def new_ticket(field_values, noi):
    """
    Create a ticket from the command line.

    The current default mode is interactive user input. That might change
    in the future. Fully non-interactive behavior can be triggered by using
    a lot of -s KEY=VALUE options in combination with --noi.

    To see which parameters exist, run jira in interactive mode and read the
    yaml file. All top level keys are valid for -s KEY=... .

    WARNING: There is no validation!
    """
    tmp = map(lambda x: x.split("=", 1), field_values)

    # pre-populate the template with values from command line
    # and default values
    replace_dict = TICKET_CREATE_DEFAULT_VALUES.copy()
    replace_dict.update({k: v for k, v in tmp})
    template, _ = process_template(TICKET_CREATE_DEFAULT_TEMPLATE,
                                   replace_dict,
                                   remove_remaining=True)

    # in interactive mode
    user_input = template
    if not noi:
        # present to user, get modified version back
        # let's use the .yaml file ending, so that syntax highlighting activates
        # if configured.
        with tempfile.NamedTemporaryFile(suffix='.yaml') as tmp:
            user_input = editor.edit(
                    # use_tty=True,
                    filename=tmp.name,
                    contents=template.encode("utf-8"))

    # convert to yaml and strip values to look nice
    create_dict = yaml.load(user_input)
    create_dict = create_dict_prep(create_dict)

    if not noi:
        print("New ticket data:")
        print(yaml.dump(create_dict, default_flow_style=False))
        print("CREATE THIS? (YES|no): ", end="")
        user = input()
        if user.lower() != "yes":
            print("Sorry, need 'yes' to start.")
            sys.exit(-1)

    # go for it
    # https://is.gd/cyFsu4
    create_dict = create_dict_jira(create_dict)
    ticket = get_jira().create_issue(fields=create_dict)
    print("{} - {}".format(ticket.key,
                           urljoin(ticket._options["server"],
                                   "browse/" + ticket.key)))


@cli.command(name="bulk-create", context_settings=CLI_HELP)
@click.argument("filename")
@click.option("--csv-dialect", default="excel",
              help="Python csv dialect to use (CSV only)")
@click.option("-t", "--filetype",
              type=click.Choice(["yaml", "json", "csv"]),
              help="For files without extension")
@click.option("--limit",
              default=0,
              help="Stop after creating N entries")
@click.option("--start-at",
              default=0,
              help="Start skip the first N entries (0-based)")
@click.option("-c", "--continue", "continue_file",
              metavar="ERRORFILE",
              default="",
              help="Specify error file name to retry only the failed tickets")
@click.option("-s", "--set", "manual_fields",
              multiple=True, metavar="FIELD=VAL",
              help="Set a field value manually. Takes precedence over "
                   "input data")
@click.option("-f", "--filter", "select_filters",
              multiple=True,
              metavar="FIELDNAME=REGEX",
              default="",
              help="Select issues based on field matches. Drop the rest.")
@click.option("-d", "--dry-run",
              is_flag=True,
              help="Print tickets which would be created, but don't do "
                   "anything")
@click.option("-p", "--print", "summary",
              is_flag=True,
              help="Print short summary of each created ticket")
@handle_errors
def bulk_create(filename, csv_dialect, filetype, limit, start_at,
                continue_file, manual_fields, select_filters, dry_run, summary):
    """
    Mass-create tickets from a JSON, CSV or YAML file. The file must contain
    flat keys and supports the following items:

    \b
    REQUIRED FIELDS
    * project       -> JIRA project key
    * issuetype     -> str
    * summary       -> str
    * description   -> str

    \b
    OPTIONAL FIELDS
    * labels        -> see below
    * duedate       -> YYYY-MM-DD
    * estimate      -> JIRA estimate string ("1d 4h")
    * epic_name     -> string for epic name
    * epic_link     -> JIRA ticket ID (XXX-123)

    \b
    EXPLICITLY UNSUPPORTED
    * anything regarding assignee and creator

    THE "LABELS" FIELD takes a comma-separated list of strings (a,b,c...),
    which is useful for CSV input. For YAML or JSON input the field can
    additionally be a list of strings.

    FOR CSV INPUT the script expects the first line of the CSV file to contain
    the field names, withOUT any leading comment sign (e.g. "#issuetype" or
    something similar).

    ALL OTHER KEYS are just passed 1:1 into the python jira.create_issue() API
    call, with empty fields (fields containing an empty string or None) being
    filtered out.


    IMPORTANT:

    There is *NO* semantic checking of field names or field values. So if you
    have missing fields, spelling errors, etc. this is not caught before
    jira-cli tries to create the tickets. The same goes for the wrong CSV
    dialect type.


    NOTE:

    If you get this error:

        AttributeError: 'list' object has no attribute 'values'

    ... you probably have a bad field configuration (e.g. "due" instead of
    "duedate"), **OR** that every single create failed (e.g. when continuing
    after an error).
    """
    check_file_present(filename)
    createme = load_and_parse_any(filename,
                                  csv_dialect=csv_dialect, filetype=filetype)
    if not isinstance(createme, list):
        print("'{}' must contain an array as top level element!"
              .format(filename))
        sys.exit(-1)

    # convert to indexes list.
    createme = [(idx, item) for idx, item in enumerate(createme)]

    # continue last operation? then take only those indexes which are
    # marked as failed in the error file
    if continue_file:
        check_file_present(continue_file)
        continue_file = yaml.load(open(continue_file, "r"))
        createme = [createme[error[0]] for error in continue_file]
        print("Selecting only {} failed tickets from last run"
              .format(len(createme)))

    # evaluate start_at and limit
    createme = createme[start_at:start_at + limit] \
        if limit else createme[start_at:]

    # apply selection filter
    for name_regex in select_filters:
        fieldname, sfilter = name_regex.split("=")
        regex = re.compile(sfilter, re.I)
        createme = list(filter(lambda x: regex.search(x[1][fieldname]),
                               createme))

    # evaluate --set FIELD=value
    if manual_fields:
        # https://stackoverflow.com/a/12739929/902327 :)
        update_dict = dict(s.split("=") for s in manual_fields)
        for item in createme:
            item[1].update(update_dict)

    # stop on dry runs
    if dry_run:
        yaml.safe_dump(createme, stream=sys.stdout, default_flow_style=False)
        sys.exit(1)

    # prepare ticket dicts
    indexes = [item[0] for item in createme]
    createme = [create_dict_jira(create_dict_prep(item[1]))
                for item in createme]

    # start
    print("Creating {} JIRA issues ... ".format(len(createme)),
          end="", flush=True)
    jira = get_jira()
    created = jira.create_issues(createme)

    # add indexes to results
    created = [(x, y) for x, y in zip(indexes, created)]

    # construct errors and successes lists with indexes
    errors = list(filter(lambda x: x[1]["error"] != None, created))
    successes = list(filter(lambda x: x[1]["error"] == None, created))

    # make successes printable
    for success in successes:
        # otherwise json complaints.
        success[1]["issue"] = str(success[1]["issue"])

    # print status
    print("done.\nCreated {} tickets, {} errors."
          .format(len(created) - len(errors), len(errors)))

    # print tickets if needed
    if summary and successes:
        print("\n{:>3}   {:>10}   {}".format("NO", "ID", "SUMMARY"))
        for ticket in successes:
            tmp = DotMap(ticket[1])
            print("{:>3}   {:>10}   {}".format(ticket[0],
                                               tmp.issue,
                                               tmp.input_fields.summary))
        print()

    # write log files
    timestamp = arrow.utcnow().format('X')
    for name, results in (("created", successes), ("errors", errors)):
        if results:
            log_file = "jira-{}.{}.yaml".format(timestamp, name)
            with open(log_file, "w") as outfile:
                outfile.write(yaml.safe_dump(results, indent=2))
            print("Wrote '{}'".format(log_file))
    if errors:
        print("You can re-try only failed tickets using: "
              "--continue {}".format(log_file))
        sys.exit(1)

    # finally done :)


def console_entrypoint():
    """
    The console entrypoint, pretty much unused.
    """
    cli()
