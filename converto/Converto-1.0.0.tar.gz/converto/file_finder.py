from __future__ import print_function
from os import path, walk
from menu import Menu


class FileFinder:
    files = list()
    extension_to_find = None
    option = None
    user_satisfied = False
    satisfied_menu = None
    _user_input = None

    def __init__(self, option, user_input=None):
        self.option = option
        self._user_input = user_input

    def get_user_input(self):
        while not self.user_satisfied:
            if self._user_input:
                user_input = self._user_input
                self._user_input = None
            else:
                user_input = self._ask_user_for_files()
            user_input = self._clean_user_input(user_input)
            if path.isfile(user_input):
                if self._file_is_right_extension(user_input):
                    self.files.append(user_input)
            elif path.isdir(user_input):
                self.files = self._find_files_from_directory(user_input)
            else:
                print("The path entered: {0} is not valid.\nRetrying...".format(user_input))
                continue
            if len(self.files) == 0:
                print("Selection must contain at least one file of extension types: {0}".format(self._get_exts_list()))
                continue
            self._ask_if_user_is_satisfied_with_files()

    def _clean_user_input(self, user_input):
        return user_input.replace(r"\ ", " ")

    def _ask_user_for_files(self):
        print("Valid input types: {0}\n".format(self._get_exts_list()))
        return raw_input("Enter the path of your file or directory of files: ").strip()

    def _find_files_from_directory(self, user_input):
        found_files = list()
        for root, dirs, files in walk(user_input):
            for f in files:
                if self._file_is_right_extension(f):
                    found_files.append(path.join(root,f))
        return found_files

    def _ask_if_user_is_satisfied_with_files(self):
        satisfied = True
        self.satisfied_menu = Menu(title = "Files to Process:\n{0}\nDoes this look right?".format(self._get_file_list()))
        self.satisfied_menu.set_options([
            ("Yes, continue", lambda: self._handle_user_satisfaction_choice(True)),
            ("No, let me try again.", lambda: self._handle_user_satisfaction_choice(False)),
            ("Add another file.", lambda: self._handle_user_satisfaction_choice(True, add_another=True)),
        ])
        self.satisfied_menu.open()

    def _handle_user_satisfaction_choice(self, satisfied, add_another=False):
        self.satisfied_menu.close()
        if add_another:
            return
        if not satisfied:
            self.files = list()
        self.user_satisfied = satisfied
        
    def _get_file_list(self):
        file_list_string = ''
        for x in self.files:
            file_list_string = file_list_string + x + "\n"
        return file_list_string 

    def _get_exts_list(self):
        extension_list_string = ''
        for x in self.option.valid_input_exts:
            extension_list_string = extension_list_string + x + ", "
        return extension_list_string[:-2]

    def _file_is_right_extension(self, file_path):
        return file_path.endswith(tuple(self.option.valid_input_exts))