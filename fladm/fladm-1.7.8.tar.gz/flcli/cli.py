#!/usr/bin/python
import os
import sys
import argparse
from flcli.fl3.auth import Auth
from flcli.fl3.hdfs import File
from flcli.fl3.oozie import OozieClient


def login(args):
    print 'login... user=%s pw=%s domain=%s' % (args.user, args.pw, args.domain)
    auth = Auth()
    auth.login(args.domain, args.user, args.pw)
    auth.save_cookie()

    if auth.validate():
        print 'Success'
    else:
        print 'Fail'
        exit(1)


def upload(args):
    print 'uploading... source=%s dest=%s permission=%s own=%s group=%s' % (args.source, args.dest, args.permission, args.own, args.group)
    auth = Auth()
    auth.load_cookie()

    file = File(auth)
    r = file.upload_file(args.source, args.dest, True)

    if args.own or args.group or args.permission:
        file.permission(args.dest, owner=args.own, group=args.group, permission=args.permission)

    if r:
        print 'Success'
    else:
        print 'Fail'
        exit(1)


def oozie_run(args):
    print 'oozie... type=%s xml_path=%s config=%s base_url=%s user=%s' % (args.type, args.xml_path, args.config, args.base_url, args.user)

    configuration = {}

    f = open(args.config, 'r')
    for line in f.read().split('\n'):
        if len(line) <= 0:
            continue

        key = line.split('=')[0].strip()
        value = line.split('=')[1].strip()
        print key, value
        configuration[key] = value

    f.close()

    oozie = OozieClient(base_url=args.base_url, user=args.user)

    if args.type == 'wf':
        job_id = oozie.run_workflow(args.xml_path, configuration=configuration)
        print (job_id)
    elif args.type == 'bd':
        job_id = oozie.run_bundle(args.xml_path, configuration=configuration)
        print (job_id)
    else:
        job_id = oozie.run_coordinator(args.xml_path, configuration=configuration)
        print (job_id)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # login
    parser_hdfs = subparsers.add_parser('login')
    parser_hdfs.add_argument('-user', help="Flamingo WEB username", required=True)
    parser_hdfs.add_argument('-pw', help="Flamingo WEB password", required=True)
    parser_hdfs.add_argument('-domain', help="Flamingo WEB domain", required=True)
    parser_hdfs.set_defaults(func=login)

    # upload
    parser_hdfs = subparsers.add_parser('upload')
    parser_hdfs.add_argument('-source', help="local filename (source)", required=True)
    parser_hdfs.add_argument('-dest', help="HDFS filename (destination)", required=True)
    parser_hdfs.add_argument('-permission', help="Permission (644|755)", default="644")
    parser_hdfs.add_argument('-own', help="Owner username 'hdfs", default="hdfs")
    parser_hdfs.add_argument('-group', help="Group name 'hdfs", default="hdfs")
    parser_hdfs.set_defaults(func=upload)

    # oozie
    parser_hdfs = subparsers.add_parser('oozie-run')
    parser_hdfs.add_argument('-type', help="workflow, coordinator, bundle (wf|cd|bd)", required=True)
    parser_hdfs.add_argument('-xml_path', help="xml path in HDFS", required=True)
    parser_hdfs.add_argument('-config', help="configuration file name", required=True)
    parser_hdfs.add_argument('-base_url', help="Oozie server base url", default="http://master2.exem.oss:11000/oozie")
    parser_hdfs.add_argument('-user', help="user", default="hdfs")
    parser_hdfs.set_defaults(func=oozie_run)

    parser.parse_args()
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == '__main__':
    main()