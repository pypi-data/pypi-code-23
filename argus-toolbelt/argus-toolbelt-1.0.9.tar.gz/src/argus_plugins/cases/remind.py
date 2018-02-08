import smtplib
import time
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from argus_cli.plugin import register_command, api
from argus_cli.helpers.log import log

from . import utils

UNASSIGNED = "unassigned"
SKIPABLES = ["tech", "assigned", "unassigned"]

DEFAULT_STATUS = utils.STATUSES[:-1]  # Exclude closed status


def _days(days: int) -> int:
    """Type check and converter to timestamp

    :param days: Days
    :returns: Today minus "days" in unix timestamp
    """
    days = int(days)
    latest = datetime.today() - timedelta(days=days)

    return int(time.mktime(latest.timetuple()))


def _get_customer_id(name: str) -> int:
    """Gets a customer's ID from their name

    :param name: The name of the customer
    """
    customers = api.Customers.V1.Customer.getCustomerByShortname(shortName=name.lower())["data"]
    customer_id = customers["id"]  # This might get the wrong customer if there are more with the same name?
    return customer_id


def parse_data(cases: list, skipable: list) -> dict:
    """Parses cases and associates them with a user

    :param cases: Cases to parse
    :param skipable: If any types of cases are skipable
    :returns: All cases sorted after the user to send to
    """
    parsed_cases = {UNASSIGNED: []}

    for case in cases:
        if case["assignedTech"] and "assigned" not in skipable:
            tech = case["assignedTech"]["userName"]

            if "tech" in skipable:
                log.info("%s: Adding case #%s" % (UNASSIGNED, case["id"]))
                parsed_cases[UNASSIGNED].append(case)
            else:
                log.info("%s: Adding case #%s" % (tech, case["id"]))
                if tech not in parsed_cases:
                    parsed_cases[tech] = []
                parsed_cases[tech].append(case)
        elif not case["assignedTech"] and "unassigned" not in skipable:
            log.info("%s: Adding case #%s" % (UNASSIGNED, case["id"]))
            parsed_cases[UNASSIGNED].append(case)
        else:
            log.info("Skipping case #%s" % case["id"])

    return parsed_cases


def create_emails(subject: str, message: str, parsed_cases: dict, notify: list) -> dict:
    """Crates emails from the parsed_cases dict

    :param subject: The subject of the email
    :param message: The boilerplate part of the email
    :param parsed_cases: The parsed cases to create emails from
    :param notify: Who to notify for unassigned cases
    :return: A mail for each user
    """
    mails = {}

    for user, cases in parsed_cases.items():
        if len(cases) is 0:
            # Don't bother generating a mail without any cases
            continue

        body = message + "\n\n"
        for case in cases:
            body +=\
                "#%s - %s - %s - Last Update: %s\n"\
                % (case["id"], case["status"], case["subject"],
                   datetime.fromtimestamp(case["lastUpdatedTimestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S"))

        mails[user] = MIMEText(body)
        mails[user]["Subject"] = subject
        mails[user]["From"] = "argus-noreply@mnemonic.no"
        mails[user]["To"] = ";".join(notify) if user == UNASSIGNED else "%s@mnemonic.no" % user

    return mails


@register_command(extending="cases")
def remind(subject: str, message: str, notify: list = None,
           service_type: utils.SERVICE_TYPES = None, status: utils.STATUSES = DEFAULT_STATUS,
           customer: _get_customer_id = None, priority: utils.PRIORITIES = None, skip: SKIPABLES = None,
           days: _days = _days(14), dry: bool = False,
           smtp_host: str = "smtp.mnemonic.no"):
    """A command for reminding people when they have pending cases that haven't been updated for a while.

    :param subject: The subject of the email
    :param message: The body of the email
    :param notify: Email(s) to notify for unassigned cases
    :param list service_type: The service type of the case
    :param list status: The status of the case
    :param customer: Customers to use (shortname)
    :param list priority: Priorities to have on the case
    :param list skip: Certain things to not notify about
    :param days: Amount of days since last activity
    :param dry: Runs the program without sending the actual email
    :param smtp_host: The SMTP host to send mail from

    :alias smtp_host: smtp
    """
    log.info("Getting cases to notify about")
    cases = api.Cases.V2.Case.advancedCaseSearch(
        limit=0,
        service=service_type, status=status, priority=priority, customerID=[customer],
        startTimestamp=days
    )["data"]

    parsed_cases = parse_data(cases, skip)

    log.info("Creating emails")
    mails = create_emails(subject, message, parsed_cases, notify or [])

    if len(mails) is 0:
        log.info("No emails to send")
    else:
        log.info("Sending email")

    for recipient, mail in mails.items():
        if dry:
            print("%s\n" % mail)
        else:
            smtp = smtplib.SMTP(smtp_host)
            smtp.send_message(mail)
            smtp.quit()
