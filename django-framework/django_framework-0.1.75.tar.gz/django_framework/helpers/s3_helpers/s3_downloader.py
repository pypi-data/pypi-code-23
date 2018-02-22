import boto
from boto.s3.key import Key


class S3StorageDownloader(object):

    def download_file_from_key(self, bucket_name, key_name, output_filename):
        
        bucket = self.conn.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
#         bucket.get_contents_as_string()
        key.get_contents_to_filename(output_filename)
        
        return True

if __name__ == '__main__':

    s3 = S3Storage(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
#     s3.generate_key_url(bucket_name='pge_greenbutton_data', key = '')
    response = s3.check_key_exists(bucket_name='utility-greenbutton-data-xml', key='photographingthemundane.pdf', folder_path = '/pge/')
    
    print(response)
