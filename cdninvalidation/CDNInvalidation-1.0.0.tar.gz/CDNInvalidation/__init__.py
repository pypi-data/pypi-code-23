#!/usr/bin/env python
# create by wanglin, at 2018.02.24, https://newops.cn

import boto3
import time

class CloudFront:
    def __init__(self, DistributionId):
        self.client = boto3.client('cloudfront') 
        self.DID = DistributionId

    def create_invalidation(self, items):
        item_list = items.split(',')
        item_num = len(item_list)

        response = self.client.create_invalidation(
            DistributionId = self.DID,
            InvalidationBatch = {
                'Paths': {
                    'Quantity': item_num,
                    'Items': item_list 
                },
                'CallerReference': str(time.time())
            }
        )

        InvalidationId = response['Invalidation']['Id']
        print "%s - Invalidation     ID : %s" % (str(time.ctime()), InvalidationId)

        return InvalidationId

    def get_invalidation(self, InvalidationId):
        response = self.client.get_invalidation(
            DistributionId = self.DID,
            Id = InvalidationId
        )

        return response['Invalidation']['Status']

    def wait_invalidation(self, InvalidationId):
        max_retries = 5
        step_timeout = 30

        for x in range(0, max_retries):
            status = self.get_invalidation(InvalidationId)
            print "%s - Invalidation status : %s" % (str(time.ctime()), status)

            if status == 'Completed':
               break
            else:
               time.sleep(step_timeout)


def main():
    import sys
    if len(sys.argv) != 3:
        print "Wrong number of argments inputed!"
        sys.exit(1)
    else:
        did = str(sys.argv[1])
        items = str(sys.argv[2])

    CF = CloudFront(did)
    InvalidationId = CF.create_invalidation(items)
    CF.wait_invalidation(InvalidationId)

if __name__ == "__main__":
    main()
