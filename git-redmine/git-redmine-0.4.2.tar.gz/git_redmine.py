#!/usr/bin/env python

# pip install --user python-redmine click

import os
import re
import git
import unidecode
import tempfile
import glob
import StringIO
import subprocess

from requests.adapters import HTTPAdapter
from redminelib import Redmine
import click

MARKER = '# Everything below is ignored\n'


def slugify(title):
    title = unidecode.unidecode(title)
    title = re.sub('[^a-zA-Z]+', '-', title)
    return title


def get_config(name, default=Ellipsis):
    repo = git.Repo()
    reader = repo.config_reader()
    if not reader.has_section('redmine'):
        raise click.UsageError('Please add a redmine section to your git configuration')
    if not reader.has_option('redmine', name):
        if default is Ellipsis:
            raise click.UsageError('Please add redmine\'s %s' % name)
        else:
            return default
    return reader.get('redmine', name)


def get_redmine_api():
    url = get_config('url')
    key = get_config('key', None)
    username = get_config('username', None)
    password = get_config('password', None)
    if not key and (not username or not password):
        raise click.UsageError('Please add a redmine\'s key or username/password')
    if key:
        kwargs = dict(key=key)
    else:
        kwargs = dict(username=username, password=password)
    redmine = Redmine(url, **kwargs)
    redmine.engine.session.mount('http://', HTTPAdapter(max_retries=3))
    redmine.engine.session.mount('https://', HTTPAdapter(max_retries=3))
    return redmine


def set_redmine(section, option, value):
    repo = git.Repo()
    config_writer = repo.config_writer()
    if not config_writer.has_section(section):
        config_writer.add_section(section)
    config_writer.set(section, option, value)
    config_writer.write()


def set_branch_option(branch, option, value):
    set_redmine('branch "%s"' % branch.name, option, value)


def get_issue(issue_number=None):
    if not issue_number:
        issue_number = get_current_issue()
    api = get_redmine_api()
    try:
        issue = api.issue.get(issue_number)
    except:
        raise click.UsageError(
                'Cannot find issue %s' % issue_number)
    return issue


def get_current_issue():
    repo = git.Repo()
    branch_name = repo.head.reference.name
    splitted = branch_name.rsplit('/', 1)
    issue_number = splitted[-1].split('-')[0]
    try:
        issue_number = int(issue_number)
    except:
        raise click.UsageError(
                'Cannot find an issue number in current branch name %s' % branch_name)
    return issue_number


def get_current_project():
    project_id = get_config('project', None)
    if not project_id:
        raise click.UsageError('No default project is set')
    api = get_redmine_api()
    return api.project.get(project_id)


def get_patches(number_of_commits=0):
    repo = git.Repo()
    tempdir = tempfile.mkdtemp()
    if number_of_commits:
        ref = 'HEAD' + '~' * number_of_commits
    else:
        ref = '@{upstream}'
    repo.git.format_patch(ref, o=tempdir)

    def helper():
        for path in glob.glob(os.path.join(tempdir, '*.patch')):
            yield {
                    'path': path,
                    'filename': os.path.basename(path),
            }
    return list(helper())


@click.group()
def redmine():
    '''Integrate git branch with redemine, you must configure your .config/git/config file
       with a [redmine] section and keys: url, key or username/password.
    '''
    pass


@redmine.group()
def issue():
    pass


@redmine.group(invoke_without_command=True)
@click.pass_context
def project(ctx):
    if ctx.invoked_subcommand is None:
        project = get_current_project()
        click.echo('Current project %s' % project)

def apply_attachments(repo, issue):
    if not issue.attachments.total_count:
        return
    print 'Currently attached patches'
    attachments = sorted(issue.attachments, key=lambda a: a.id)
    for i, attachment in enumerate(attachments):
        print i, attachment.created_on, '%6d bytes' % attachment.filesize, attachment.filename
    while True:
        indexes = click.prompt('Which patch would you like to apply (id separated by spaces) ?', type=str)
        try:
            indexes = map(int, indexes.split())
            if not all(i < len(attachments) for i in indexes):
                raise ValueError('invalid values', indexes)
        except Exception as e:
            print 'error:', e
            continue
        else:
            break
    for index in indexes:
        attachment = attachments[index]
        content = attachment.download().content
        try:
            p = repo.git.execute(['git', 'am'], istream=subprocess.PIPE, as_process=True)
            p.communicate(content)
        except Exception as e:
            print e
            print 'Applying patch', index, attachment.filename, 'failed, please fix it.'
            break


@issue.command()
@click.argument('issue_number')
def take(issue_number):
    '''Create or switch to a branch to fix an issue'''
    api = get_redmine_api()
    issue = api.issue.get(issue_number, include='attachments')
    repo = git.Repo()
    new = False
    for head in repo.heads:
        if '/%s-' % issue_number in head.name:
            branch_name = head.name
            branch = head
            break
    else:
        new = True
        branch_name = 'wip/%s-%s' % (issue_number, slugify(issue.subject))
        click.confirm(
            'Do you want to create branch %s tracking master ?' % branch_name,
            abort=True)
        branch = repo.create_head(branch_name)
        set_branch_option(branch, 'merge', 'refs/heads/master')
        set_branch_option(branch, 'remote', '.')
    if repo.head.reference == branch:
        click.echo('Already on branch %s' % branch_name)
    else:
        branch.checkout()
        click.echo('Moved to branch %s' % branch_name)
    if new:
        apply_attachments(repo, issue)


@issue.command()
@click.option('--issue', default=None, type=int)
def apply(issue):
    issue = get_issue(issue)
    repo = git.Repo()
    apply_attachments(repo, issue)


@issue.command()
@click.option('--issue', default=None, type=int)
def show(issue):
    issue = get_issue(issue)
    click.echo('URL: %s' % issue.url)
    click.echo('Subject: %s' % issue.subject)
    click.echo('Description: %s' % issue.description)
    click.echo('')
    journals = list(issue.journals)
    if journals:
        click.echo('Last note by %s: ' % journals[-1].user)
        click.echo('%s' % journals[-1].notes)


@issue.command()
@click.option('--issue', default=None, type=int)
@click.argument('number_of_commits', default=0)
def submit(issue, number_of_commits):
    '''Submit current patch from this issue branch to Redmine'''
    issue = get_issue(issue)
    patches = get_patches(number_of_commits)
    message = '\n\n' + MARKER
    for patch in patches:
        message += '\n%s' % patch['filename']
    message = click.edit(message)
    if message is not None:
        message = message.split(MARKER, 1)[0].rstrip('\n')
    api = get_redmine_api()
    api.issue.update(issue.id, notes=message, uploads=patches)


@issue.command()
@click.pass_context
def new(ctx):
    '''Create a new issue in the default project of this repository'''
    project = get_current_project()
    api = get_redmine_api()
    subject_and_description = click.edit('Enter subject on first line\n\nand notes after.') \
        .splitlines()
    subject, description = subject_and_description[0], '\n'.join(subject_and_description[1:])
    subject = subject.strip()
    description = description.strip()
    current_user = api.user.get('current')
    click.echo('Project: %s' % project)
    click.echo('Subject: %s' % subject)
    click.echo('Description: %s' % description)
    click.echo('Assigned to: %s' % current_user)
    if click.confirm('Create issue ?'):
        issue = api.issue.create(
                project_id=project.id,
                subject=subject,
                description=description,
                assigned_to_id=current_user.id)
        click.echo('Created issue %s' % issue.url)
        ctx.invoke(take, issue_number=issue.id)


@project.command()
@click.argument('project_id')
def set(project_id):
    '''Set default redmine project for this git repository'''
    api = get_redmine_api()
    try:
        api.project.get(project_id)
    except:
        raise click.UsageError('Project %s is unknown' % project_id)
    repo = git.Repo()
    config_writer = repo.config_writer()
    if not config_writer.has_section('redmine'):
        config_writer.add_section('redmine')
    config_writer.set('redmine', 'project', project_id)
    config_writer.write()


if __name__ == '__main__':
    redmine()
