import boto3
import botocore
import os
import uuid
import json
import sys
import time
from boto3.s3.transfer import S3Transfer
from navio.aws.services._session import AWSSession
from navio.aws import shared
from navio.aws._common import dump

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

shared.store['validated_templates'] = list()


class AWSCloudFormation(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(
            kwargs.get('profile_name'),
            kwargs.get('region_name', None)
        )
        self.stack_name = kwargs['stack_name']

        if (len(kwargs) == 2 and
                'profile_name' in kwargs and
                'stack_name' in kwargs):
            # Easy service, for lookups only
            self.easy_service = True
        elif (len(kwargs) == 3 and
              'profile_name' in kwargs and
              'stack_name' in kwargs and
              'region_name' in kwargs):
            # Easy service, for lookups only
            self.easy_service = True
        else:
            self.easy_service = False

            self.on_failure = kwargs.get('on_failure', 'ROLLBACK')

            if 'template' in kwargs and type(kwargs['template']) == str:
                self.template = kwargs['template']
            else:
                raise Exception('Missing or wrong parameter: template')

            self.includes = list()
            if 'includes' in kwargs:
                if type(kwargs['includes']) == list:
                    self.includes = kwargs['includes']
                else:
                    raise Exception('Wrong parameter type: '
                                    'includes = {}'.format(
                                        type(kwargs['includes'])))

            self.resources = list()
            if 'resources' in kwargs:
                if type(kwargs['resources']) == list:
                    self.resources = kwargs['resources']
                else:
                    raise Exception('Wrong parameter type: '
                                    'resources = {}'.format(
                                        type(kwargs['resources'])))

            if 'parameters' in kwargs:
                self.parameters = kwargs['parameters']
            else:
                self.parameters = None

            self.template = os.path.abspath(os.path.join(
                os.getcwd(), './src/main/cloudformation/', self.template))
            for idx, template in enumerate(self.includes):
                if not os.path.isabs(template):
                    if template.startswith('./') or template.startswith('../'):
                        self.includes[idx] = os.path.abspath(
                            os.path.join(os.getcwd(), template))
                    else:
                        self.includes[idx] = os.path.abspath(os.path.join(
                            os.getcwd(),
                            './src/main/cloudformation/',
                            template
                        ))

                if not os.path.isfile(self.includes[idx]):
                    raise Exception("Can't find template file"
                                    " '{}' ({})".format(
                                        template,
                                        self.includes[idx]))

            for idx, file in enumerate(self.resources):
                if not os.path.isabs(file):
                    if file.startswith('./') or file.startswith('../'):
                        self.resources[idx] = os.path.abspath(
                            os.path.join(os.getcwd(), file))
                    else:
                        self.resources[idx] = os.path.abspath(
                            os.path.join(
                                os.getcwd(),
                                './src/main/resources/',
                                file
                            ))

                if not os.path.isfile(self.resources[idx]):
                    raise Exception("Can't find resource file "
                                    "'{}' ({})".format(
                                        file, self.resources[idx]))

            url = urlparse(kwargs['s3_uri'])
            self.s3_bucket = url.netloc
            self.s3_key = url.path

            if self.s3_key.endswith('/'):
                self.s3_key = "%s%s" % (
                    self.s3_key, os.path.basename(self.template))

            if self.s3_key.startswith('/'):
                self.s3_key = self.s3_key[1:]

    # @property
    # def s3_uri(self):
    #   return self._s3_uri

    def exists(self):
        cloudformation = self.session.client('cloudformation')
        STACK_EXISTS_STATES = [
            'CREATE_COMPLETE',
            'ROLLBACK_COMPLETE',
            'UPDATE_COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE'
        ]
        try:
            stack = None
            nextToken = None
            while not stack:
                resp = None
                if nextToken:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name, NextToken=nextToken)
                else:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name)

                for stack in resp['Stacks']:
                    if stack['StackStatus'] in STACK_EXISTS_STATES:
                        return True
                if 'NextToken' in stack:
                    nextToken = stack['NextToken']

            return False
        except botocore.exceptions.ClientError as err:
            err_msg = err.response['Error']['Message']
            err_code = err.response['Error']['Code']
            if (err_msg != "Stack with id {} does not exist".format(
                    self.stack_name) and
                    err_code != 'ValidationError'):
                return False

    def outputs(self, output_key, **kwargs):
        return self.output(output_key, **kwargs)

    def output(self, output_key, **kwargs):
        cloudformation = self.session.client('cloudformation')
        STACK_EXISTS_STATES = [
            'CREATE_COMPLETE',
            'ROLLBACK_COMPLETE',
            'UPDATE_COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE'
        ]

        no_fail = False
        if kwargs:
            no_fail = kwargs.get('no_fail', False)

        try:
            stack = None
            nextToken = None
            while not stack:
                resp = None
                if nextToken:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name, NextToken=nextToken)
                else:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name)

                for stack in resp['Stacks']:
                    if stack['StackStatus'] in STACK_EXISTS_STATES:
                        break
                if 'NextToken' in stack:
                    nextToken = stack['NextToken']

            # output_value = None
            if 'Outputs' in stack:
                for output in stack['Outputs']:
                    if output['OutputKey'] == output_key:
                        return output['OutputValue']
        except botocore.exceptions.ClientError as err:
            err_msg = err.response['Error']['Message']
            err_code = err.response['Error']['Code']
            if (err_msg != "Stack with id {} does not exist".format(
                    self.stack_name) and
                    err_code != 'ValidationError'):
                if no_fail:
                    print("Stack with id "
                          "{} does not exist".format(self.stack_name))
                else:
                    raise Exception("Stack with id {} does not exist".format(
                        self.stack_name), sys.exc_info()[2])

        print("Can't find output parameter %s in stack %s under %s profile" %
              (output_key, self.stack_name, self.profile_name))
        return None

    def validate(self, details=False):
        s3 = self.session.client('s3')
        for template in ([self.template] + self.includes):

            if template in shared.store['validated_templates']:
                print('Template {} has been validated already'.format(
                    template
                ))
                continue
            else:
                shared.store['validated_templates'].append(template)

            temp_filename = "temp/%s-%s" % (uuid.uuid4(),
                                            os.path.basename(template))
            print("Uploading %s to temporary location s3://%s/%s" %
                  (template, self.s3_bucket, temp_filename))
            S3Transfer(s3).upload_file(
                template,
                self.s3_bucket,
                temp_filename,
                extra_args={'ACL': 'bucket-owner-full-control'}
            )

            template_url = "https://s3.amazonaws.com/%s/%s" % (
                self.s3_bucket, temp_filename)
            print("Validating template %s" % template_url)
            resp = self.session.client('cloudformation').validate_template(
                TemplateURL=template_url
            )

            if details:
                print('Template {} details: {}'.format(
                    template,
                    json.dumps(resp, indent=2, separators=(',', ': '))))

            print("Removing temporary file /%s from s3" % temp_filename)
            s3.delete_object(
                Bucket=self.s3_bucket,
                Key=temp_filename,
            )

    def create(self, **kwargs):
        self._upload()

        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)
        print("Creating stack {}".format(stack_name))
        resp = cloudformation.create_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure=self.on_failure,
            Parameters=self._join_parameters(
                self.parameters, kwargs.get('parameters', None))
        )

        waiter = cloudformation.get_waiter('stack_create_complete')
        waiter.wait(
            StackName=resp['StackId']
        )

        return

    def update(self, **kwargs):
        self._upload()

        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)
        print("Updating stack {}".format(stack_name))
        resp = cloudformation.update_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=self._join_parameters(
                self.parameters, kwargs.get('parameters', None))
        )

        waiter = cloudformation.get_waiter('stack_update_complete')
        waiter.wait(
            StackName=resp['StackId']
        )

        return

    def delete(self, **kwargs):
        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        cloudformation.delete_stack(
            StackName=stack_name
        )

        waiter = cloudformation.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def wait_complete(self, **kwargs):
        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status complete'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_create_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def wait_update(self, **kwargs):
        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status updated'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_update_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def wait_delete(self, **kwargs):
        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status deleted'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def dry_run(self, **kwargs):
        self._upload()

        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)

        change_set_name = 'cs{ts}'.format(ts=time.strftime('%Y%m%d%H%M%S'))
        client_token = 'token{uuid}'.format(uuid=uuid.uuid4())

        print("Running dry_run for stack {}".format(stack_name))
        change_set = cloudformation.create_change_set(
            StackName=stack_name,
            ChangeSetName=change_set_name,
            ClientToken=client_token,
            ChangeSetType='UPDATE',
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=self._join_parameters(
                self.parameters,
                kwargs.get('parameters', None)
            )
        )
        waiter = cloudformation.get_waiter('change_set_create_complete')
        try:
            waiter.wait(
                StackName=stack_name,
                ChangeSetName=change_set_name
            )

            print('Changes to be performed:')
            next_token = None
            while True:
                args = {
                  'StackName': stack_name,
                  'ChangeSetName': change_set['Id'],
                }
                if next_token:
                    args['NextToken'] = next_token

                resp = cloudformation.describe_change_set(**args)

                for change in resp['Changes']:
                    print('{action}: {id} - {res_type}'.format(
                            action=change['ResourceChange']['Action'],
                            id=change['ResourceChange']['LogicalResourceId'],
                            res_type=change['ResourceChange']['ResourceType'],
                        )
                    )

                if 'NextToken' not in resp:
                    break
                else:
                    next_token = resp['NextToken']

        except botocore.exceptions.WaiterError as error:
            if error.kwargs['reason'] == ('Waiter encountered a '
               'terminal failure state'):
                resp = cloudformation.describe_change_set(
                    StackName=stack_name,
                    ChangeSetName=change_set['Id'],
                )
                if resp['StatusReason'] == (
                      "The submitted information "
                      "didn't contain changes. "
                      "Submit different information "
                      "to create a change set."
                      ):
                    print("No changes.")
                else:
                    raise Exception("Unknown error", None, sys.exc_info()[2])
            else:
                raise Exception("Unknown error", None, sys.exc_info()[2])
        finally:
            cloudformation.delete_change_set(
                StackName=stack_name,
                ChangeSetName=change_set['Id']
            )

        return

    def estimate_cost(self, **kwargs):
        self._upload()

        cloudformation = self.session.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/{}/{}".format(
            self.s3_bucket, self.s3_key)
        print("Estimating template s3://{}/{}".format(
            self.s3_bucket, self.s3_key
        ))
        resp = cloudformation.estimate_template_cost(
            TemplateURL=template_url,
            Parameters=self._join_parameters(
                self.parameters, kwargs.get('parameters', None))
        )

        print('Check URL to see your template costs estimateion:\n{}'.format(
            resp['Url']))

        return

    def _upload(self):
        print("Uploading %s to s3://%s/%s" %
              (self.template, self.s3_bucket, self.s3_key))
        S3Transfer(self.session.client('s3')).upload_file(
            self.template,
            self.s3_bucket,
            self.s3_key,
            extra_args={'ACL': 'bucket-owner-full-control'}
        )

        s3_key = self.s3_key
        if not s3_key.endswith('/'):
            s3_key = s3_key[:s3_key.rfind('/')+1]

        for file in (self.includes + self.resources):
            file_s3_key = '{}{}'.format(s3_key, os.path.basename(file))

            print("Uploading %s to s3://%s/%s" %
                  (file, self.s3_bucket, file_s3_key))
            S3Transfer(self.session.client('s3')).upload_file(
                file,
                self.s3_bucket,
                file_s3_key,
                extra_args={'ACL': 'bucket-owner-full-control'}
            )

    def _join_parameters(self, params1, params2):
        if (
            (params1 and type(params1) != list) or
            (params2 and type(params2) != list)
        ):
            raise Exception("Parameters argument should be a list() or None")

        if not params1 and params2:
            return params2
        elif params1 and not params2:
            return params1
        elif params1 and params2:
            result_d = dict()
            for param in params1:
                result_d[param['ParameterKey']] = param['ParameterValue']
            for param in params2:
                result_d[param['ParameterKey']] = param['ParameterValue']

            result = list()
            for key in result_d:
                result.append({
                    'ParameterKey': key,
                    'ParameterValue': result_d[key]
                })
            return result
        else:
            return list()
