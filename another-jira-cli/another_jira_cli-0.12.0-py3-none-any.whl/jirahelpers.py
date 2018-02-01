import sys
from functools import lru_cache, wraps

import arrow
import jira

from .tools import cfg_read_config, cfg_save_search


# ============================================================================
# DECORATORS
# ============================================================================


def catch_jira_errors(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except jira.exceptions.JIRAError as e:
            print("JIRA ERROR: {}".format(e.text))
            sys.exit(-1)
    return inner


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


@lru_cache()
def get_jira():
    """
    Creates the global jira object, cached.

    :return: The JIRA object instance to use for JIRA calls.
    """
    config = cfg_read_config()
    jobj = jira.JIRA(config['jira_url'],
                     basic_auth=(config['username'],
                                 config['password']))
    return jobj


def check_for_alias(ticket_alias_str, no_output=False):
    """
    Checks whether the ticket string is an alias, if yes resolves it, if
    no returns it unchanged.

    :param ticket_alias_str: The potential ticket alias
    :param no_output: No output please
    :return: The input or the resolved alias
    """
    config = cfg_read_config()
    if "aliases" in config and ticket_alias_str in config["aliases"]:
        # we have an alias, use it.
        ticket = config["aliases"][ticket_alias_str]
        if not no_output:
            print("Resolving alias '{}' to ticket {}"
                  .format(ticket_alias_str, ticket))
        return ticket
    else:
        return ticket_alias_str


def get_worklogs_for_date_and_user(date, user=None) -> list:
    """
    Retrieves all work logs for a given user on a given day. Returns a
    list of the form: [[TICKET_OBJ, [WORKLOG0,...], ...]

    The date object does not need to point to the start of the day.

    :param date: The date to search worklogs for
    :param user: The user to search worklogs for
    :return: The dict as described above
    """
    if not user:
        # we can't use currentUser() cause we want to filter for the user
        # name later. "currentUser()" is not a user name :(
        config = cfg_read_config()
        user = config["username"]

    # get the tickets logged by our user on this date
    jira = get_jira()
    date_str = date.format("YYYY-MM-DD")
    jql_query = 'worklogDate = "{}" and worklogAuthor in ({})'\
                .format(date_str, user)

    # create a [(ticket_obj, worklog_LIST), ...] list
    worklogs = [(ticket, jira.worklogs(ticket.key))
                for ticket in jira.search_issues(jql_query)]

    # this gives us all ticket objects the user added worklogs to on the
    # given time, so the *tickets* are filtered by our expression. the
    # *worklogs* attached to the tickets though are not. so we need to
    # sort out all worklogs which are not on the desired day, and not
    # from the specified author.

    # flatten this - [(ticket, ONE_worklog), ...]
    worklogs = [(t, l) for t, logs in worklogs for l in logs]

    # now, filter this. unfortunately the started datetime is a STRING :((
    # so two lines below this we convert this to an arrow object to make
    # comparison ... not potentially buggy.
    lb, ub = date.floor('day'), date.ceil('day')
    worklogs = list(filter(lambda x: x[1].author.name == user and
                                     lb <= arrow.get(x[1].started) <= ub,
                           worklogs))

    # return [(ticket_obj, worklog_obj), ...]
    return worklogs


@lru_cache()
def get_ticket_object(ticket_str, no_output=False):
    """
    Returns a ticket object from a ticket key or a defined alias. The alias
    name has preference if somebody named an alias after a ticket.

    Will throw an exception if the alias or ticket can't be found.

    :param ticket_str: The ticket key or alias name.
    :param no_output: Whether to be silent while doing it.
    :return: A JIRA issue object
    """
    ticket_str = check_for_alias(ticket_str)
    jira = get_jira()
    ticket_obj = jira.issue(ticket_str)
    return ticket_obj


def add_worklog(ticket_str, use_datetime, worklog, comment,
                no_output=False):
    """
    Wrapper to add a timelog to JIRA. Mainly used to resolve a possible
    ticket alias in the process.

    :param ticket_str: The ticket identifier as string
    :param use_datetime: A datetime object with the start time and date
    :param worklog: The worklog time as used in JIRA (e.g. "1h 30m")
    :param comment: An optional comment
    :param no_output: If we should be silent
    :return:
    """
    jira = get_jira()
    ticket_obj = get_ticket_object(ticket_str, no_output)
    jira.add_worklog(ticket_obj,
                     started=use_datetime,
                     timeSpent=worklog,
                     comment=comment)


def perform_search(jql):
    jira = get_jira()
    results = jira.search_issues(jql)
    print("# {:<10} {:<20} {}".format("key", "author", "summary"))
    for result in results:
        sum = result.fields.summary
        aut = str(result.fields.reporter)
        use_sum = sum if len(sum) < 70 else sum[:67] + "..."
        use_aut = aut if len(aut) < 20 else aut[:17] + "..."
        print("{:<12} {:<20} {}".format(result.key, use_aut, use_sum))


def search_wrapper(searchstring, save_as, just_save):
    if not just_save:
        perform_search(searchstring)
    if save_as:
        cfg_save_search(save_as, searchstring)


# ===========================================================================
# BULK-CREATE HELPERS
# ===========================================================================

def _bk_label_converter(labels):
    if isinstance(labels, str):
        rv = list(map(lambda x: x.strip(), filter(None, labels.split(","))))
    else:
        rv = labels
    return rv


tdict = {
    #format:
    # field name:   (target field name,     conversion function)
    "labels":       ("labels",              _bk_label_converter                                 ),
    "project":      ("project",             lambda v: {"key": v}                                ),
    "issuetype":    ("issuetype",           lambda v: {"name": v[0].upper() + v[1:].lower()}    ),
    "estimate":     ("timetracking",        lambda v: {"originalEstimate": v}                   ),
    "epic_link":    ("customfield_10018",   lambda v: v                                         ),
    "epic_name":    ("customfield_10020",   lambda v: v                                         ),
}

def construct_create_dict(input_dict):
    """
    returns the dict object which can be used to create the jira issue
    using the API.

    understands the following keys:

      - labels (comma separated list)
      - due (iso date)
      - estimate (jira estimate string)
      - issuetype
      - project
      - epic_name
      - epic_link

    all other fields are simply taken as-is.
    """
    create = {}
    for k, v in input_dict.items():
        if k in tdict:
            newkey, conv_func = tdict[k]
            create[newkey] = conv_func(v)
        else:
            create[k] = v

    # filter out empty values
    create = {k: v for k, v in create.items() if v}

    return create


def construct_jql_string_from_saved_searches(search_strings):
    """
    Takes a list of jira JQL strings, and creates a resulting JQL search
    string from it by combining all the original ones.

    ORDER BY clauses are handled by using the last one encountered (right
    now, the requirement is that max. 1 ORDER BY clause should be present
    in the original search strings).

    Basically the resulting string is:

    (SEARCH1) [AND (SEARCH2)...] [ORDER BY last-order-by-clause]

    :param search_strings: A list of JQL search strings
    :return: A final JQL search string
    """

    def transf(x):
        idx = x.lower().find("order by")
        if idx > -1:
            return x[:idx].strip()
        else:
            return x

    order_clause = ""

    # extract "the" order clause
    for search_string in search_strings:
        idx = search_string.lower().find("order by")
        if idx > -1:
            order_clause = search_string[idx:].strip()

    # two steps in one: map strings and filter out empty ones
    use_queries = filter(lambda x: x, map(transf, search_strings))

    # add brackets around each string to combine with AND later
    use_queries = map(lambda x: "(" + x + ")", use_queries)

    # join them :)
    jql_string = " AND ".join(use_queries) + " " + order_clause

    # done, return.
    return jql_string.strip()
