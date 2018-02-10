import boto
from boto.s3.key import Key

class S3StorageUploader(object):

    BASE_URL = "https://s3.amazonaws.com/"
    
    # LIST of allowed policies from:
#     https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html
    ALLOWED_POLICIES = ["public-read", "authenticated-read", "bucket-owner-read", "private"]
    DEFAULT_POLICY = "public-read"
    
    ALLOWED_BUCKETS = None
    
    
    def generate_key_url(self, bucket_name, key, folder_path = None, expires_in = None, validate = True):
        if validate == True:
            if self.check_key_exists(bucket_name = bucket_name, key = key, folder_path = folder_path) == False:
                raise ValueError('You cannot generate a url without the key existing')

        if expires_in is None:
            expires_in = self.DEFAULT_EXPIRES_IN
        if folder_path is not None:
            key = folder_path  + '/' + key
            
        url = self.conn.generate_url(expires_in, 'GET', bucket_name, key)

        return url
    
    def save_file(self, bucket_name, input_filename, output_filename, folder_path = None, policy = None, expires_in = None):
        '''Please ensure that the input_filename and output_filename are both just the filename!
        the folder_path can be multiple deep but should not have prepended or trailing slashes
        
        input_filename is the file that is being saved to s3
        output_filename is the filename that s3 will save it under.  in some cases itll be the same but it doesnt need to be.
        '''
        if expires_in == None:
            expires_in = self.DEFAULT_EXPIRES_IN

        if policy == None:
            policy =  self.DEFAULT_POLICY
            
        if policy not in self.ALLOWED_POLICIES:
            raise ValueError('You are trying to set permissions that you shouldnt be')
        
        
        if self.ALLOWED_BUCKETS != None and bucket_name not in self.ALLOWED_BUCKETS:
            raise ValueError('You are trying to write to a bucket that you cannot access')

        if folder_path is not None:
            output_filename = folder_path + '/' + output_filename
            

        bucket = self.conn.get_bucket(bucket_name)
    
        key = Key(bucket)
        key.key = output_filename
        ss = key.set_contents_from_filename(input_filename, policy=policy)
        
        hosted_url = self.BASE_URL + bucket_name + "/" + key.key
        
        # returns the hosted url
        # returns a url for the file that will expire in 1 hour.
        return hosted_url, key.generate_url(expires_in= expires_in, query_auth=False)
    
    
    def save_file_from_obj(self, bucket_name, input_filename, output_filename, folder_path = None, policy = None):
        '''Please ensure that the input_filename and output_filename are both just the filename!
        the folder_path can be multiple deep but should not have prepended or trailing slashes
        
        input_filename is the file that is being saved to s3
        output_filename is the filename that s3 will save it under.  in some cases itll be the same but it doesnt need to be.
        '''
        if policy == None:
            policy =  self.DEFAULT_POLICY
            
        if policy not in self.ALLOWED_POLICIES:
            raise ValueError('You are trying to set permissions that you shouldnt be')
        
        
        if self.ALLOWED_BUCKETS != None and bucket_name not in self.ALLOWED_BUCKETS:
            raise ValueError('You are trying to write to a bucket that you cannot access')

        if folder_path is not None:
            output_filename = folder_path + '/' + output_filename
            
        try:    
            bucket = self.conn.create_bucket(bucket_name)
        except Exception as e:
            bucket = self.conn.get_bucket(bucket_name)

        key = Key(bucket)
        key.key = output_filename
        

        ss = key.set_contents_from_file(input_filename, policy=policy)
        
        hosted_url = self.BASE_URL + bucket_name + "/" + key.key
        
        # returns the hosted url
        # returns a url for the file that will expire in 1 hour.
        return hosted_url, key.generate_url(expires_in= self.DEFAULT_EXPIRES_IN, query_auth=False)

    
    def save_file_stream(self, bucket_name, input_filestream, output_filename, policy = "public-read"):
        raise ValueError()
    
    
    

if __name__ == '__main__':

    s3 = S3Storage(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
#     s3.generate_key_url(bucket_name='pge_greenbutton_data', key = '')
    response = s3.check_key_exists(bucket_name='utility-greenbutton-data-xml', key='photographingthemundane.pdf', folder_path = '/pge/')
    
    print(response)
