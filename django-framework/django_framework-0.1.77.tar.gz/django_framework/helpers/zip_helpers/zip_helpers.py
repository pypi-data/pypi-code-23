import os
import zipfile
from zipfile import ZipFile


class FileZip(object):
    
    
    def zip_files(self, zip_filename, filenames, remove_files = True):
        '''Put a list of files in filenames into a zip file called zip_filename,
        then remove the files in filenames
        '''
        success = True
        error = None
        with ZipFile(zip_filename, 'w') as myzip:
            for filename in filenames:
                myzip.write(filename, compress_type = zipfile.ZIP_DEFLATED)
        
        if remove_files == True:
            self.remove_files(filenames = filenames)
            
        return zip_filename
    
    
    def unzip(self, zip_filename, remove_files = True):
        
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
    
#     z.zip_files('output2.zip', ['test.py'], remove_files = True)
    z.unzip('output.zip', remove_files = True)
if __name__ == '__main__':
    main()