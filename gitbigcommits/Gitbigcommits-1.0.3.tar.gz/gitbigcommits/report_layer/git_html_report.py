from Cheetah.Template import Template
from datetime import datetime
from gitbigcommits.core.git_commit_utility import GitFatCheckutility
import os
import sys
import pkg_resources
import logging

logging.basicConfig()

def get_output_list(git_folder=None, threshold_size=None):
    '''

    :param git_folder: Location of git repo folder.
    :param threshold_size: size in KB
    :return: list of dictionary with all info

    This will generate a list of the big commits in your
    repo. The input to the methos is your git directory,
    and the threshold file size.

    It can be set in the  enviornmental variable "GIT_FOLDER_DIR" and
    "GIT_FILE_SIZE"
    eg:
    export GIT_FOLDER_DIR="usr/home/myrepo/"
    export GIT_FILE_SIZE="1024"   size is in Kb
    '''
    if not git_folder:
        if (len(sys.argv)) != 3:
            print ('''Format should be:: bigcommits-html "<GitFolderPath>"
             <ThresholdSize> \n GitFolderPath denotes where ".git" folder is
             present''')
            return
        args = sys.argv[1:]
        git_folder = args[0]
        threshold_size = args[1]

    git_utility = GitFatCheckutility(git_folder, threshold_size)
    list_of_large_files = git_utility.get_all_file_with_info()
    return list_of_large_files


def console_output():
    '''

    :return: None

    The output will be printed in the std output
    This will be called when the command-line command `cygitcheck` is invoked.

    use: cygitcheck <GitFolderPath> <ThresholdSize>
    GitFolderPath denotes where ".git" folder is
         present

    Eg: cygitcheck '/usr/home/viswesh/myrepo' 1024

    '''
    if (len(sys.argv)) != 3:
        print ('''Format should be:: bigcommits "<GitFolderPath>"
         <ThresholdSize> \n GitFolderPath denotes where ".git" folder is 
         present''')
        return
    args = sys.argv[1:]
    folder_to_check = args[0]
    size = args[1]

    list_of_large_files = get_output_list(folder_to_check, size)
    for row in list_of_large_files:
        for key, val in row.items():
            print (key, ":", val)
        print ("\n")


def fat_html_output():
    """
    This writes the output into a html file 'git_fat_files.html'.

    """
    list_of_large_files = get_output_list()

    template_name = os.getenv("FAT_TEMPLATE_NAME", "fat_file_user_info.html")
    template_path = pkg_resources.resource_filename("gitbigcommits.miscellaneous",
                                                    template_name)

    template = Template(file=template_path,
                        searchList=[{
                            'TODAY_DATE': datetime.now().strftime('%Y-%m-%d'),
                            'LIST_OF_BIGFILES': list_of_large_files
                        }
                        ])

    with open('git_fat_files.html', 'w') as html_file:
        html_file.write(str(template))

    print("Successfully generated html, file name is : %s" % template_name)


def dorm_branch_html_output():
    '''
    This is to find the dormant branch present in your repo.

    Input to this method is two environmental variables.
        1)GIT_FOLDER_DIR
        2)GIT_DORMANT_TIME default value is 50 days. set to 0 to find all branch
    info
    :return: None4320000
    '''

    if (len(sys.argv)) != 3:
        print ('''Format should be:: dbranch-html "<GitFolderPath>"
         <ThresholdSize> \n GitFolderPath denotes where ".git" folder is
         present''')
        return
    args = sys.argv[1:]
    git_folder = args[0]
    dormant_time = args[1]
    git_utility = GitFatCheckutility(git_folder, "1")
    dormant_time = float(dormant_time if dormant_time else "4320000")
    branch_list_info = git_utility.domant_branch_info(dormant_time)
    template_name = os.getenv("DORM_BRANCH_TEMPLATE_NAME",
                              "dorm_branch_info.html")
    template_path = pkg_resources.resource_filename(
        "gitbigcommits.miscellaneous",
                                                    template_name)

    template = Template(file=template_path,
                        searchList=[{
                            'TODAY_DATE': datetime.now().strftime('%Y-%m-%d'),
                            'LIST_OF_BRANCHINFO': branch_list_info
                        }
                        ])

    with open('git_dorm_branch.html', 'w') as html_file:
        html_file.write(str(template))

    print("Successfully generated html, file name is : %s" % template_name)

