

def lookup(service, value, region=None):
    if service == 'kms':
        from aws_boto3.kms import get_alias_attr
        alias = get_alias_attr(value, return_attr='ALL', region=region)
        if alias:
            arn = alias["AliasArn"].split(':')
            arn.pop()
            arn.append('key/{}'.format(alias["TargetKeyId"]))
            return ':'.join(arn)
