import os
import zipfile
from zipfile import ZipFile


class FileZip(object):
    
    
    def zip_files(self, zip_filename, filenames, remove_files = True, allow_zip_64 = False):
        '''Put a list of files in filenames into a zip file called zip_filename,
        then remove the files in filenames
        '''
        success = True
        error = None
        with ZipFile(zip_filename, 'w', allowZip64=allow_zip_64, compression=zipfile.ZIP_DEFLATED) as myzip:
            for filename in filenames:
                myzip.write(filename)
        
        if remove_files == True:
            self.remove_files(filenames = filenames)
            
        return zip_filename
    
    
    def unzip(self, zip_filename, remove_files = True, allow_zip_64 = False):
        
        name_list = None
        with ZipFile(zip_filename, 'r') as myzip:
            # printing all the contents of the zip file
            myzip.printdir()
            name_list = myzip.namelist()
            
            # extracting all the files
            print('Extracting all the files now...')
            myzip.extractall()
            print('Done!')
        
        if remove_files == True:
            self.remove_files(filenames = [zip_filename])
        
        return name_list
    
    def remove_files(self, filenames):
        
        for filename in filenames:
            os.remove(filename)

def main():
    z = FileZip()
    
    z.zip_files('output2.zip', ['download_files/test/test.csv'], remove_files = False, allow_zip_64= True)
#     z.unzip('download_all_datastream_uclachai.zip', remove_files = False)
if __name__ == '__main__':
    main()