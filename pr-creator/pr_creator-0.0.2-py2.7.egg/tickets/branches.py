import logging
import subprocess

logger = logging.getLogger(__name__)

apps = ["eab_base", "student-path", "notification-service", "greendale"]


def change_reqs_files(app, args):
    if app in ["eab_base", "notification-service"]:
        return

    if args.local:
        files_cmd = "grep  -l '.*.txt$' -r $PROJECTS/{app}/requirements/local.txt".format(app=app)
    else:
        files_cmd = "grep  -l '.*.txt$' -r $PROJECTS/{app}/requirements/*".format(app=app)
    files_to_change = filter(lambda x: x != "", subprocess.check_output(files_cmd, shell=True).split('\n'))

    for file_to_change in files_to_change:
        logger.info('Changing {file}'.format(file=file_to_change))

        cmd = "sed -i \'\' -E \"s|(git@github\.com/advisory/eab_base\.git@)[^\#]+|\\1{br}|g\" {file}".format(
            br=args.branch_name,
            file=file_to_change)
        subprocess.call(cmd, shell=True)

        cmd = "sed -i \'\' -E \"s|(git@github\.com/advisory/student-path\.git@)[^\#]+|\\1{br}|g\" {file}".format(
            br=args.branch_name,
            file=file_to_change)
        subprocess.call(cmd, shell=True)


def add_and_commit(app, msg):
    cmd = "git -C $PROJECTS/{app} add .".format(app=app)
    subprocess.call(cmd, shell=True)

    cmd = 'git -C $PROJECTS/{app} commit -m "{0}"'.format(app=app, msg=msg)
    subprocess.call(cmd, shell=True)


def git_exec(app, cmd):
    cmd = "git -C $PROJECTS/{app} {cmd}".format(app=app, cmd=cmd)
    subprocess.call(cmd, shell=True)


def simple_slugify(name):
    return name.lower().strip().replace(' ', '-')


def branch_name(args):
    return "{ticket_type}/{ticket_id}-{ticket_name}".format(ticket_name=simple_slugify(args.ticket_name),
                                                            ticket_type=args.ticket_type, ticket_id=args.ticket_id)
