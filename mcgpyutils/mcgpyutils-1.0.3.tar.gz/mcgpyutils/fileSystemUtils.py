import os
import errno

class FileSystemUtils:
    def __init__(self):
        self.input_location = ""
        self.output_location = ""
        self.config_location = ""


    '''
    Sets the location of input files.  Creates the path if it does not exist.

    @param full_path: the full path to the location of input files
    '''
    def set_input_location(self, full_path):
        self.prepare_path(full_path)
        self.input_location = full_path


    '''
    Returns the location of input files.

    @return: the location of input files
    '''
    def get_input_location(self):
        return self.input_location


    '''
    Sets the location of output files.  Creates the path if it does not exist.

    @param full_path: the full path to the location of output files
    '''
    def set_output_location(self, full_path):
        self.prepare_path(full_path)
        self.output_location = full_path


    '''
    Returns the location of output files.

    @return: the location of output files
    '''
    def get_output_location(self):
        return self.output_location


    '''
    Sets the location of config files.  Creates the path if it does not exist.

    @param full_path: the full path to the location of config files
    '''
    def set_config_location(self, full_path):
        self.prepare_path(full_path)
        self.config_location = full_path


    '''
    Returns the location of config files.

    @return: the location of config files
    '''
    def get_config_location(self):
        return self.config_location


    '''
    Returns the full path to the given @script.  This should generally be called
    with the __file__ variable as @script.

    @param script: the script file
    @return: the path to the given script
    '''
    def get_path_to_script(self, script):
        return os.path.dirname(os.path.abspath(script))


    '''
    Returns a file name without its extension.

    @param path: the path to the file
    @return: the file name without its extension
    '''
    def get_file_name(self, path):
        return os.path.basename(os.path.splitext(path)[0])


    '''
    Returns a file name with its extension.

    @param path: the path to the file
    @return: the file name with its extension
    '''
    def get_file_name_with_ext(self, path):
        return os.path.basename(path)


    '''
    Ensures the given path exists.  If it does not, all missing directories are
    created.

    @param path: the path to the file or directory
    @raise OSError: raises an exception
    '''
    def prepare_path(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e: # Guard against race condition
                if e.errno != errno.EEXIST:
                    raise


    '''
    Checks to see if the given file exists.

    @param path: the path to the file
    @return: True if the path is a file and it exists
    '''
    def file_exists(self, path):
        return os.path.isfile(path)


    '''
    Checks to see if the given directory exists.

    @param path: the path to the directory
    @return: True if the given path is a directory and it exists
    '''
    def directory_exists(self, path):
        return os.path.isdir(path)


if __name__ == "__main__":
    fsu = FileSystemUtils()

    print(fsu.get_path_to_script(__file__))

    fsu.set_input_location("/tmp/input")
    fsu.set_output_location("/tmp/output")
    fsu.set_config_location("/tmp/config")

    print(fsu.get_input_location())
    print(fsu.get_output_location())
    print(fsu.get_config_location())

    print(fsu.get_file_name("{0}/{1}".format(fsu.get_path_to_script(__file__), __file__)))
    print(fsu.get_file_name_with_ext(__file__))

    print("True: " + str(fsu.file_exists("{0}/{1}".format(fsu.get_path_to_script(__file__), __file__))))
    print("False: " + str(fsu.file_exists("{0}/FILE_THAT_DOES_NOT_EXIST.txt".format(fsu.get_path_to_script(__file__)))))

    print("True: " + str(fsu.directory_exists(fsu.get_input_location())))
    print("False: " + str(fsu.directory_exists("{0}/DIR_THAT_DOES_NOT_EXIST".format(fsu.get_path_to_script(__file__)))))
