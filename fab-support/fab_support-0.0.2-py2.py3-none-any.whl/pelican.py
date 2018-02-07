# -*- coding: utf-8 -*-
"""fab_support
This is a supporting file for use with fabric.

It supports depoloying Pelican projects to a number of different environments.
The environments are defined in a STAGES dictionary which has a number of required
entries and some that can be added for the particular used case.

1) It supports a local .env file importing for storing secrets that you don't want to store in git.

In the root fabfile create a dictionary like this which documents how to deploy each stage

STAGES = {
    'localhost': {
        'comment': 'Local build and serving from output directory',
        'destination': '',
        'copy_method': copy_null,
    },
    'harddisk': {
        'comment': 'For serving locally on this computer in another directory. ',
        'destination': 'C:/Sites/www.drummond.info',
        'copy_method': copy_file,
    },
    'production': {
        'destination': 'W:/www.drummond.info',
        'copy_method': copy_file,
    },
}
"""


import boto3
import datetime as dt
from distutils.dir_util import copy_tree
import mimetypes
import os
import shutil
import sys
import socketserver
import time

from dotenv import load_dotenv, find_dotenv
from fabric.api import run, local, env, settings, cd, task, put, execute
from fabric.operations import require
from fabric.utils import abort, warn
from unipath import Path, DIRS

from pelican.server import ComplexHTTPRequestHandler


@task
def build():
    """Build version of site ready for use locally or deployment to main site eg fab local build"""
    require('stage')
    copy_images()
    local(f'pelican -s {env.config_file}')


@task
def copy_images(alias='ci'):
    """Copy files in all images directories"""
    src = Path(env.deploy_path).ancestor(2).child('content')
    dst = src.ancestor(2).child('images')
    for my_dir in src.walk(filter=DIRS):  # os.walk('./..'):
        if my_dir.name == 'images':
            copy_tree(my_dir, dst)


@task
def rebuild():
    """`build` with the delete switch"""
    require('stage')
    local(f'pelican -d -s {env.config_file}')


@task
def regenerate():
    """Automatically regenerate site upon file modification"""
    require('stage')
    local('pelican -r -s {env.config_file}')


@task
def serve():
    """Serve site at eg http://localhost:8000/"""
    require('stage')
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', env['PORT']), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(env['PORT']))
    server.serve_forever()


@task
def reserve():
    """`build`, then `serve`"""
    build()
    serve()


@task
def deploy():
    """Publish to stage. includes build."""
    require('stage')
    build()
    print(f'Using copy from {env.deploy_path} to {env.destination}')
    env['copy_method'](env.deploy_path, env.destination)
    # ? clean()
    # copy_tree(DEPLOY_PATH, LOCAL_SITE_PATH)
    # copy_tree(DEPLOY_PATH.ancestor(2).child(
    #     'Pelican').child('pelican-bootstrap3').child('static'),
    #                 LOCAL_SITE_PATH.child('static'))
    # copy_tree(DEPLOY_PATH.ancestor(1).child(
    #     'content').child('images'),
    #                 LOCAL_SITE_PATH.child('images'))


@task
def clean():
    """Remove newly generated files from remote environment"""
    require('stage')
    if os.path.isdir(env.destination):
        shutil.rmtree(env.destination)
        os.makedirs(env.destination)

        # ?try:
        #    shutil.rmtree(LOCAL_SITE_PATH)
        # except FileNotFoundError:
        #    pass  # doesn't exist


@task
def s3_upload():
    """Publish to S3"""
    rebuild()
    # get an access token, local (from) directory, and S3 (to) directory
    # from the command-line
    #local_directory = Path(normpath('./output'))
    local_directory = Path('./output').norm()
    print('Local directory = {}',format(local_directory))
    bucket = S3_BUCKET

    client = boto3.client('s3')

    # enumerate local files recursively
    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = Path(root, filename).norm()
            print('Local path = {}', format(local_path))
            # construct the full S3 path
            s3_path = '/'.join(local_directory.rel_path_to(local_path).components())[1:]
            print('Searching for path "{}" in "{}" for {}'.format(s3_path, bucket, local_path))
            try:
                file = client.head_object(Bucket=bucket, Key=s3_path)
                lt = dt.datetime.utcfromtimestamp(local_path.mtime())
                #print('Local time {} and external time {}'.format(lt,file['LastModified']))
                print("Path found on S3! Skipping {} which has {}...".format(s3_path, file['LastModified']))

                try:
                    client.delete_object(Bucket=bucket, Key=s3_path)
                    print("Uploading %s..." % s3_path)
                    mime_type = mimetypes.guess_type(local_path)
                    client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                               'ACL': 'public-read'})
                except:
                    print("Unable to delete %s..." % s3_path)
            except:
                print("Uploading %s..." % s3_path)
                mime_type = mimetypes.guess_type(local_path)
                client.upload_file(local_path, bucket, s3_path, ExtraArgs={'ContentType': mime_type[0],
                                                                           'ACL': 'public-read'})
    # s3cmd sync $(OUTPUTDIR)/ s3://$(S3_BUCKET) --acl-public --delete-removed --guess-mime-type --no-mime-magic --no-preserve




@task
def gh_pages():
    """Publish to GitHub Pages"""
    rebuild()
    local("ghp-import -b {github_pages_branch} {deploy_path} -p".format(**env))

__all__ = []
