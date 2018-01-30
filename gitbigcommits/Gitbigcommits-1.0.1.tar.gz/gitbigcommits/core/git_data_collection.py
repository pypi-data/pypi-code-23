import subprocess
import logging

logger = logging.getLogger(__name__)


class CommitInfo(object):
    """
    .. py:class:: CommitInfo
    This is just a object to hold a commit id related info. This is used i
    nternally.

    This object contains the following variables
    author: author of the commid id
    email: mail id of the committer
    subject: subject of the commit id
    timestamp: time when the commit happened
    """

    def __init__(self, author, email, subject, timestamp):
        self.author = author
        self.email = email
        self.subject = subject
        self.timestamp = timestamp


class GitFatFiles(object):
    """
    .. py:class:: GitFatFiles

    :param folder_path: git folder path, where the .git directory is
    present
    :param file_size: threshold file size
    """

    def __init__(self, folder_path, file_size=25000):

        self.folder_path = folder_path
        self.threshold_size = file_size
        self.branch_list = self.__get_remote_branch_list()
        self.all_commit_ids = self.__get_all_commit_ids_all_branches()
        self.blob_commit_dict = self.__form_blob_dict_associated_with_commit()
        self.blob_id_file_dict = self.get_all_objects_list_in_git()
        self.commit_branch_dict = self.get_commit_ids_for_a_branch()
        self.blob_size_in_bytes = dict()

    def __get_remote_branch_list(self):
        """

        :return: all remote branch list
        """
        branch_list = list()
        command = '''git for-each-ref --format='%(refname)' refs/remotes/'''
        remote_brnaches = self.get_subprocess(command, shell=True)
        for branch_name in remote_brnaches.split('\n')[:-1]:
            branch_list.append(branch_name)
        return branch_list

    def get_blob_ids_from_pack_file(self):
        """
        :return: list of blob ids which are greater than given specified size.

        This unpacks all the index file and find the size of each blob ids.
        """
        blob_id_size_list = list()
        command = '''git verify-pack -v .git/objects/pack/pack-*.idx |
        grep 'blob' | awk '$3>''' + str(self.threshold_size) + '''' |
        sort -k3nr'''
        blob_ids = self.get_subprocess(command, shell=True)
        for line in blob_ids.split('\n')[:-1]:
            blob_info = line.split()
            blob_hash = blob_info[0]
            blob_size_compressed = blob_info[2]
            self.blob_size_in_bytes[blob_hash] = blob_size_compressed
            blob_id_size_list.append((blob_hash, blob_size_compressed))
        return blob_id_size_list

    def find_info_for_a_commit_id(self, commit_sha):
        """

        :param commit_sha: hashid of a commit
        :return: author_name, author_email, subject of commit, timestamp of
        commit will be returned.

        Change this method if you need more info from a commit id
        """
        command = '''git show --quiet --pretty='%ae&$%an&$%s&$%ct' {0}''' \
            .format(commit_sha)
        commit_obj_info = self.get_subprocess(command, shell=True)
        for line in commit_obj_info.split('\n')[:-1]:
            commit_infos = line.split('&$')
            author_email = commit_infos[0]
            author_name = commit_infos[1]
            subject = commit_infos[2]
            unix_time_stamp = commit_infos[3]
            ci_obj = CommitInfo(author_name, author_email, subject,
                                unix_time_stamp)
            break
        return ci_obj

    def find_blob_for_a_commit(self, commit_hash):
        """

        :param commit_hash: hashid of a commit object
        :return: all blobids which are referenced/poined by this commit object
        also it returns a dict of mapping between blobid vs file names.
        """
        blob_file_dict = dict()
        blob_id_list = []
        command = '''git ls-tree -r {0}'''
        branch_blob_list = self.get_subprocess(command.format(commit_hash),
                                               shell=True)
        for line in branch_blob_list.split('\n')[:-1]:
            blob_info = line.split()
            blob_id = blob_info[2]
            blob_id_list.append(blob_id)
            file_name = blob_info[3]
            blob_file_dict[blob_id] = file_name

        return blob_file_dict, blob_id_list

    def __get_all_commit_ids_all_branches(self):
        """

        :return: commit ids across all branches.
        """
        command = '''git rev-list --all'''
        commit_id_list = list()
        all_commit_ids = self.get_subprocess(command, shell=True)
        for commit_id in all_commit_ids.split('\n')[:-1]:
            commit_id_list.append(commit_id.rstrip('\n'))
        return commit_id_list

    def __form_blob_dict_associated_with_commit(self):
        """

        :return: a dictionary where key is a blob id and value is a list of
        commit ids associated with that blob_id.
        """
        commit_list = self.all_commit_ids
        blob_commit_dict = dict()
        for commit_id in commit_list:
            tmp, blob_id_list = self.find_blob_for_a_commit(commit_id)
            for blob in blob_id_list:
                if blob in blob_commit_dict:
                    commit_list_tmp = blob_commit_dict[blob]
                    commit_list_tmp.append(commit_id)
                    blob_commit_dict[blob] = commit_list_tmp
                else:
                    commit_list_tmp = list()
                    commit_list_tmp.append(commit_id)
                    blob_commit_dict[blob] = commit_list_tmp
        return blob_commit_dict

    def get_commit_ids_for_a_branch(self):
        """

        :return: dictionary where commit_id is the key, and branch name as
        value.

        it is applicable only for all the remote branches
        """
        commit_branch_dict = dict()
        command = '''git rev-list {0} ^refs/remotes/origin/master'''
        for branch in self.branch_list:
            command_with_branch = command.format(branch)
            commit_ids = self.get_subprocess(command_with_branch, shell=True)
            for commit_id in commit_ids.split('\n')[:-1]:
                commit_branch_dict[commit_id] = branch

        commit_branch_dict = self._add_commit_ids_for_master_branch(
            commit_branch_dict)
        return commit_branch_dict

    def get_commit_list_for_a_branch(self, branch_name):
        """

        :param branch_name: branch name
        :return: list of commit ids associated with the branch
        """
        list_of_commit_ids = list()
        command = '''git rev-list {0} ^refs/remotes/origin/master'''
        command_with_branch = command.format(branch_name)
        commit_ids = self.get_subprocess(command_with_branch, shell=True)
        for commit_id in commit_ids.split('\n')[:-1]:
            list_of_commit_ids.append(commit_id)
        return list_of_commit_ids

    def _add_commit_ids_for_master_branch(self, commit_branch_dict):
        command = '''git rev-list refs/remotes/origin/master'''
        commit_ids = self.get_subprocess(command, shell=True)
        for commit_id in commit_ids.split('\n')[:-1]:
            commit_branch_dict[commit_id] = 'refs/remotes/origin/master'
        return commit_branch_dict

    def get_all_objects_list_in_git(self):
        """

        :return: dictionary which contains all object ids as key(blob, commit)
        the value maybe none if it is a commit id, if it is a blob id,
        value is name of the file where the blobid points to.
        """
        command = '''git rev-list --all --objects'''
        sha1_file_dict = dict()
        object_list = self.get_subprocess(command, shell=True)
        for line in object_list.split('\n')[:-1]:
            object_info = line.split()
            sha1 = object_info[0]
            if len(object_info) > 1:
                sha1_file_dict[sha1] = object_info[1]
            else:
                sha1_file_dict[sha1] = None
        return sha1_file_dict

    def get_subprocess(self, command, shell=False):
        """

        :param command: command to execute in shell
        :param shell: if set to true, can cause code injection.
        :return: output of the command
        """
        output_process = subprocess.Popen(command, shell=shell,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=self.folder_path
                                          )
        stdout, stderr = output_process.communicate()
        self._check_error(stderr, command)
        return stdout

    def _check_error(self, stderr, command):
        if stderr:
            logger.error(command)
            logger.error(stderr)
            raise StandardError(stderr)
