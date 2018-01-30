import os
from cloudctl.process import execute


def set_aws_profile(aws_profile_name):
    os.environ['AWS_PROFILE'] = aws_profile_name
    execute(f'mfa -r {aws_profile_name}', quiet=True)
