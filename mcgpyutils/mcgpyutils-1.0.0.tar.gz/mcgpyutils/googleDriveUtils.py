import os
import errno
import httplib2
import argparse

from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from .fileSystemUtils import FileSystemUtils

class GoogleDriveUtils:
    '''
    @param fsu: a mcgpyutils.fileSystemUtils object, defaults to a new object
    @param args: argparse object from calling script, defaults to None
    '''
    def __init__(self, fsu = FileSystemUtils(), args = None):
        if args is None:
            self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        else:
            self.flags = args
        self.fsu = fsu
        self.credentials = self.get_google_drive_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.drive_service = discovery.build('drive', 'v3', http=self.http)


    '''
    Retrieves credential information if the files do not exist in the config
    directory.

    @return: Google Drive credentials object
    @raise FileNotFoundError: config/google_drive_client_secret.json is missing
    '''
    def get_google_drive_credentials(self):
        google_drive_config = "{0}/google_drive_config.json".format(self.fsu.get_config_location())
        google_drive_client_secret = "{0}/google_drive_client_secret.json".format(self.fsu.get_config_location())

        if not os.path.exists(google_drive_config):
            open(google_drive_config, "w")

        if not os.path.exists(google_drive_client_secret):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), google_drive_client_secret)

        store = Storage(google_drive_config)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(google_drive_client_secret, "https://www.googleapis.com/auth/drive")
            flow.user_agent = "Cordova Build Uploader"
            credentials = tools.run_flow(flow, store, self.flags)

        return credentials


    '''
    Retrieves the file id of the first match of a given file name.

    @param file_name: the name of the file to search for
    @return: associated id, None if no file was found
    '''
    def get_google_drive_file_id(self, file_name):
        response = self.drive_service.files().list(q="name='{0}'".format(file_name), spaces='drive', fields='files(id, name)').execute()

        for file in response.get('files', []):
            return file.get('id')

        return None


    '''
    Retrieves all files matching a given name.

    NOTE: A file still exists until it is permanently deleted from the "TRASH"
    folder on Google Drive.  It takes a short period of time to process after
    it is permanently deleted.

    @param file_name: the file_name to search for
    @return: a collection of Google Drive file objects
    '''
    def get_files_by_name(self, file_name):
        return self.drive_service.files().list(q="name='{0}'".format(file_name), spaces="drive", fields="files(id, name)").execute()


    '''
    Retrieves all children files under the given ID.

    @param parent_id: the id of the directory to search under
    @return: a collection of Google Drive file objects
    '''
    def get_children_files(self, parent_id):
        return self.drive_service.files().list(q="'{0}' in parents".format(parent_id), spaces="drive", fields="files(id, name)").execute()


    '''
    Creates a new file on Google Drive.

    @param formatted_name: the name that will appear in Google Drive
    @param parent_id: the id of the directory to create the file in
    @param path: the local path leading to the file to be uploaded
    @param raw_name: the name of local file to be uploaded
    @param mime_type: the MIME type of the file to be uploaded
    @return: a Google Drive file object of the file that was created
    '''
    def create_google_drive_file(self, formatted_name, parent_id, path, raw_name, mime_type):
        file_metadata = {"name": formatted_name, "parents": [parent_id]}
        media = MediaFileUpload("{0}/{1}".format(path, raw_name), mimetype=mime_type)
        return self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()


    '''
    Updates an exiting file on Google Drive.  A new version will be added.

    @param formatted_name: the name that will appear in Google Drive
    @param file_id: the id of the file to update
    @param path: the local path leading to the file to be uploaded
    @param raw_name: the name of local file to be uploaded
    @param mime_type: the MIME type of the file to be uploaded
    @return: a Google Drive file object of the file that was updated
    '''
    def update_google_drive_file(self, formatted_name, file_id, path, raw_name, mime_type):
        file_metadata = {"name": formatted_name}
        media = MediaFileUpload("{0}/{1}".format(path, raw_name), mimetype=mime_type)
        return self.drive_service.files().update(body=file_metadata, media_body=media, fileId=file_id).execute()


    '''
    Creates a new folder on Google Drive

    @param folder_name: the name of the folder to create
    @param parent_id: the id of the parent folder to place the new folder,
                      defaults to None (Google Drive root)
    @return: the id of the folder that was created
    '''
    def create_google_drive_folder(self, folder_name, parent_id = None):
        # Create a folder on Drive, returns the newely created folder ID
        body = {
          "name": folder_name,
          "mimeType": "application/vnd.google-apps.folder"
        }

        if parent_id:
            body["parents"] = [parent_id]

        root_folder = self.drive_service.files().create(body=body).execute()
        return root_folder["id"]
