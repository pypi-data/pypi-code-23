#!/usr/bin/env python2.7

'''
DESCRIPTION: Functions to talk with google app engine from local.

NOTES:
    - Make sure the os environment flag is not operating. 
'''

import os


#$$# gsutil_rsync_file_to_cloud_storage #$$#
def gsutil_cp_rsync_file_to_cloud_storage(filePathIn, filePathOut, singleFile=False):
    '''
    DESCRIPTION: 
        - Creates a directory for the files in the app default bucket. 
        - Can copy an entire directory at a time. 
        - rsyncs if singleFile=False
        - copies if singleFile=True
    
    USES:
        - During the initial setup of the webapp - copying the figures from local directories to cloud storage.
    
    NOTES:
        - Use a multithreaded approach.
        - Files will be copied with rsync
        - To overwrite - one must include -d as an option?
        - #Instead of copying directories at a time, it might be better if we just copy the files that we are interested in. 
    '''
    if singleFile:
        cmd = ["gsutil",  "cp",  filePathIn, filePathOut] #Command with -n - does not overwrite
    else:
        cmd = ["gsutil", "-m", "rsync", "-r", filePathIn, filePathOut] #Command with -n - does not overwrite
    print(cmd)
    os.system(" ".join(cmd))

#$# gsutil_rsync_file_to_cloud_storage #$#

# "gs://" + self.appId + ".appspot.com/" + dataset.setKey
#########################
#########################
#DEPRACATED COMMANDS#
    #WARNING: When uploading new files to the Cloud Storage directory - need to make sure that there is no subdirectory with the same name that exists. Otherwise, it will place the directory in that location. 
#    See https://cloud.google.com/storage/docs/gsutil/commands/cp
#        - Search "subdirectory exists"
#    cmd = ["gsutil", "-m", "cp", "-n", "-r", dataset.imageDir, "gs://" + self.appId + ".appspot.com/" + dataset.setKey] #Command with -n - does not overwrite
