import boto3
import botocore
import os
import shutil
import zipfile
from boto3.s3.transfer import S3Transfer
from navio.aws.services._session import AWSSession
from navio.aws._common import execute, ls, which
from subprocess import check_call, CalledProcessError
from datetime import datetime

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


class AWSLambda(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(kwargs['profile_name'])
        self.profile_name = kwargs['profile_name']
        self.function_name = kwargs['function_name']

        if 'pip_requirements' in kwargs:
            self.pip_requirements = kwargs['pip_requirements']
        else:
            self.pip_requirements = list()

        self.s3_filename = kwargs['s3_filename']

        url = urlparse(kwargs['s3_uri'])
        self.s3_bucket = url.netloc
        self.s3_key = url.path

        if self.s3_key.endswith('/'):
            self.s3_key = "%s%s" % (
                self.s3_key, os.path.basename(self.s3_filename))

        if self.s3_key.startswith('/'):
            self.s3_key = self.s3_key[1:]

    def validate(self):
        self.install_deps(['--user'])
        errors = list()
        files = ls('./src/main/python', '*.py')

        if not which('pylint'):
            print('pylint command not found,'
                  ' skipping code validation via PyLint')
            return True

        if len(files) == 0:
            print("No python files for validation")
            return True
        else:
            print("Validating files via pylint: %s" % files)

        for filename in files:
            try:
                execute('pylint', '--extension-pkg-whitelist=pymssql',
                        '--errors-only', filename)
            except Exception as e:
                errors.append(filename)

        if len(errors) > 0:
            print("There are errors in python files: %s" % errors)
            raise Exception(
                "Lambda validation error. Check output for details.")

        return True

    def package(self):
        print('[ Packaging lambda deployment package ]')
        shutil.rmtree('target/distrib/', ignore_errors=True)

        files = ls('src/main/python/', '*.py')
        cwd = os.getcwd()
        print('[ Files ]')
        for name in files:
            print(name[len(cwd)+1:])

        shutil.copytree('src/main/python/', 'target/distrib/',
                        ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))

        self.install_deps(['--target', 'target/distrib/'])

        zipf = zipfile.ZipFile(
            'target/{}'.format(self.s3_filename), 'w', zipfile.ZIP_DEFLATED)
        # with safe_cd('target/distrib/')
        basedir_len = len(os.path.abspath(
            os.path.join(os.getcwd(), 'target/distrib')))
        for name in ls('target/distrib/'):
            zipf.write(name, name[basedir_len:])
        zipf.close()

        return True

    def install_deps(self, pip_args=None):
        print('[ Installing lambda dependencies ]')
        print('[ Dependencies ]')

        args = ['install', '--upgrade']

        if pip_args:
            if type(pip_args) != list:
                raise "pip_args argument should be of a list() type"

            for pip_arg in pip_args:
                if pip_arg == '--user' and os.getenv('VIRTUAL_ENV', False):
                    # skip --user when inside virtualenv
                    pass
                else:
                    args.append(pip_arg)

        for req in self.pip_requirements:
            print('Installing {}'.format(req))
            execute('pip', args, req)

        if not self.pip_requirements or len(self.pip_requirements) == 0:
            print("Your lambda doesn't have any pip dependencies")

    def upload(self):
        s3 = self.session.client('s3')
        lambda_package = os.path.normpath(os.path.join(
            os.getcwd(), 'target/', self.s3_filename))
        print("Uploading %s to temporary location s3://%s/%s" %
              (lambda_package, self.s3_bucket, self.s3_key))
        S3Transfer(s3).upload_file(
            lambda_package,
            self.s3_bucket,
            self.s3_key,
            extra_args={'ACL': 'bucket-owner-full-control'}
        )

    def update_code(self, **kwargs):
        lambdas = self.session.client('lambda')
        if kwargs and 'function_name' in kwargs:
            function_name = kwargs['function_name']
        else:
            function_name = self.function_name
        print("Updating function {name} "
              "code from s3://{bucket}/{key}".format(
                  name=function_name,
                  bucket=self.s3_bucket,
                  key=self.s3_key))
        resp = lambdas.update_function_code(
            FunctionName=function_name,
            S3Bucket=self.s3_bucket,
            S3Key=self.s3_key,
            Publish=False
        )

    def update_dev_alias(self):
        lambdas = self.session.client('lambda')
        print('Updating function {} DEV alias to version $LATEST'.format(
            self.function_name))
        lambdas.update_alias(
            FunctionName=self.function_name,
            FunctionVersion='$LATEST',
            Name='DEV',
            Description='Updated by pynt at {} UTC'.format(
                datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S"))
        )

        pass

    def update_prod_alias(self):
        lambdas = self.session.client('lambda')
        resp = lambdas.publish_version(
            FunctionName=self.function_name,
        )

        print('Updating function {} PROD alias to version {}'.format(
            self.function_name, resp['Version']))
        lambdas.update_alias(
            FunctionName=self.function_name,
            FunctionVersion=resp['Version'],
            Name='PROD',
            Description='Updated by pynt at {} UTC'.format(
                datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S"))
        )

    def test_local(self, event={}, **kwargs):
        lambdas = self.session.client('lambda')
        if kwargs and 'function_name' in kwargs:
            function_name = kwargs['function_name']
        else:
            function_name = self.function_name
        resp = lambdas.get_function(
            FunctionName=function_name
        )

        sep = resp['Configuration']['Handler'].rfind('.')
        py_file_name = resp['Configuration']['Handler'][:sep]
        py_method_name = resp['Configuration']['Handler'][sep+1:]

        import logging
        logging.basicConfig()
        logger = logging.getLogger('lambda')
        logger.setLevel('DEBUG')

        import sys
        import platform
        if platform.system() == 'Windows':
            sys.path.append('src\main\python')
        else:
            sys.path.append('src/main/python')

        import importlib
        mod = importlib.import_module(py_file_name)
        result = getattr(mod, py_method_name)(event, {})
