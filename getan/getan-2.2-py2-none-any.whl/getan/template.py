# -*- coding: utf-8 -*-
#
# (c) 2014 by Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.

# import logging
import os.path
import sys

from datetime import date, datetime, timedelta

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader

from getan.backend import Backend, DEFAULT_DATABASE

# logging.basicConfig(level='DEBUG')  # quick fix until getan-eval.py offers it
# logger = logging.getLogger()


def human_time(delta):
    days = delta.days
    seconds = days * 3600 * 24
    s = seconds + delta.seconds
    h = s / 3600
    m = (s % 3600) / 60
    if (s % 60) >= 30:
        m += 1
        if m == 60:
            m = 0
            h += 1
    return "%d:%02d" % (h, m)


def date_format(d):
    return d.strftime("%d.%m.%Y")


def duration(entries):
    total = timedelta(0)
    for entry in entries:
        total += entry.get_duration()
    return total


def unix_week(week, year=None):
    """Convert iso week to unix week

    For unix week see man date "%W"
    Args:
        week: Week number as int to convert
        year: Year as int. If year is none the current year is used.
    """
    if not year:
        year = datetime.now().year
    firstday = date(year, 1, 4)
    isoweek = firstday.isocalendar()[1]
    unixweek = int(firstday.strftime("%W"))
    diff = isoweek - unixweek
    return week - diff


def render(template, database=None, year=None, week=None, project=None,
           user=None, empty_projects=True):
    if not user:
        user = os.getenv("USER") or "USER"

    if not database:
        if os.path.isfile(DEFAULT_DATABASE):
            database = os.path.abspath(DEFAULT_DATABASE)
        else:
            database = os.path.expanduser(os.path.join("~", ".getan",
                                                       DEFAULT_DATABASE))
    if not os.path.isfile(database):
        print >> sys.stderr, "'%s' does not exist or is not a file." % database
        sys.exit(1)

    u_week = None

    c_year = int(date.today().strftime("%Y"))
    c_week = datetime.now().isocalendar()[1]

    if week is not None and year is None:
        year = c_year

    if not os.path.isfile(database):
        print >> sys.stderr, "'%s' does not exist or is not a file." % database
        sys.exit(1)

    loader = ChoiceLoader([FileSystemLoader(os.path.expanduser(os.path.join(
        "~", ".getan", "templates"))),
        PackageLoader("getan")])

    env = Environment(loader=loader)
    env.filters["human_time"] = human_time
    env.filters["date_format"] = date_format
    env.filters["duration"] = duration

    template_name = template or "wochenbericht"
    template = env.get_template(template_name)

    backend = Backend(database)

    if not project:
        projects = backend.load_projects()
    else:
        project = backend.load_project(project)
        projects = [project]

    if year is not None or week is not None:
        u_week = "%02d" % unix_week(week, year)
        for project in projects:
            project.load_entries(year, u_week)

    if not empty_projects:
        projects = [project for project in projects if project.entries]

    entries = []
    for project in projects:
        entries.extend(project.entries)

    context = dict()
    context["entries"] = entries
    context["project"] = project
    context["projects"] = projects
    context["user"] = user
    context["database"] = database
    context["year"] = year
    context["week"] = week
    context["current_week"] = c_week
    context["current_year"] = c_year
    context["unix_week"] = u_week
    context["total_time"] = duration(entries)
    context["today"] = date.today()
    return template.render(context)
