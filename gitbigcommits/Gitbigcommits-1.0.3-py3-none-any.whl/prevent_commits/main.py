import argparse
import os
import sys
import shutil
import subprocess
import pkg_resources

argument_parser = argparse.ArgumentParser(
    description="Prevents git large commits")
argument_parser.add_argument(
    '-p', '--git_path', help='Git root folder', required=True)


def get_subprocess_output(command, git_path=".", shell=False):
    output_process = subprocess.Popen(command, shell=shell,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      cwd=git_path)
    stdout, stderr = output_process.communicate()
    if stderr:
        print (stderr)
        sys.exit(1)
    return stdout


def copy_to_git_directory(git_path):
    full_path = pkg_resources.resource_filename(__name__, "pre-commit")
    shutil.copy(full_path, git_path)


def give_permission(git_path):
    get_subprocess_output(['chmod', '+x', 'pre-commit'],
                          git_path=git_path)


def install_script():
    if (len(sys.argv)) != 2:
        print ('''Format should be:: <command> "<GitFolderPath>"
        \n GitFolderPath denotes where ".git" folder is
         present''')
        return
    args = sys.argv[1:]
    git_folder = args[0]
    full_path = git_folder + "/.git/hooks/"
    if not os.path.isdir(full_path):
        print ("Not a valid git directory..")
        sys.exit(1)
    copy_to_git_directory(full_path)
    give_permission(full_path)
    print ("\nSuccessfully Installed git pre-commit script\n" \
          "--------------------------------------------\n--------------H" \
          "appy Commits-----------------")
