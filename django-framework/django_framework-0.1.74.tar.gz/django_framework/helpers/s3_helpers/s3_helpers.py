import boto
from boto.s3.key import Key


from s3_uploader import S3StorageUploader
from s3_downloader import S3StorageDownloader

class S3Storage(S3StorageUploader, S3StorageDownloader):

    BASE_URL = "https://s3.amazonaws.com/"
    
    ALLOWED_POLICIES = ["public-read", "authenticated-read", "bucket-owner-read"]
    DEFAULT_POLICY = "public-read"
    
    ALLOWED_BUCKETS = None
    
    DEFAULT_EXPIRES_IN = 3600
    
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        
        self.conn = boto.connect_s3(self.aws_access_key_id, self.aws_secret_access_key)
    
    
    
    def check_key_exists(self, bucket_name, key, folder_path = None):
        if folder_path is not None:
            # even if folder_path has trailing backslash, s3 is ok, true for initial backslash as well
            key = folder_path  + '/' + key
            
        # will error out if no bucket of that name
        bucket = self.conn.get_bucket(bucket_name)
        possible_key = bucket.get_key(key)

        return possible_key != None  # true if it exists, false otherwise


if __name__ == '__main__':

    s3 = S3Storage(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
#     s3.generate_key_url(bucket_name='pge_greenbutton_data', key = '')
    response = s3.check_key_exists(bucket_name='utility-greenbutton-data-xml', key='photographingthemundane.pdf', folder_path = '/pge/')
    
    print(response)
