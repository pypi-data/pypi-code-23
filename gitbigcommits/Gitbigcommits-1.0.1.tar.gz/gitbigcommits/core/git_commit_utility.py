from gitbigcommits.core.git_data_collection import GitFatFiles, CommitInfo
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ExtraCommitInfo(CommitInfo):
    """
    .. py:class:: ExtraCommitInfo
    This class hold info related to the commit object.
    """

    def __init__(self, last_commit_info_obj, diff_time, branch_name,
                 first_commit_info=None):
        self.last_commit_obj = last_commit_info_obj
        self.diff_time = diff_time
        self.branch_name = branch_name
        self.first_commit_obj = first_commit_info

    def __cmp__(self, other):
        return other.diff_time - self.diff_time


class GitFatCheckutility(GitFatFiles):
    """
    .. py:class:: GitFatCheckutility

    :param git_folder_path: Directory of your git repo
    :param threshold_size_in_kb: The size which you consider as big commits, given in kb.
    """

    def __init__(self, git_folder_path, threshold_size_in_kb):

        super(GitFatCheckutility, self).__init__(
            git_folder_path, threshold_size_in_kb * 1024)

    def get_commits_for_a_blob(self, blob_sha):
        """
        :param blob_sha: hashid of a blob object
        :return: all commit ids which has reference/points to that blob
        """
        return self.blob_commit_dict.get(blob_sha)

    def get_file_name_for_blob_id(self, blob_sha):
        """

        :param blob_sha: hashid of a blob object
        :return: file name of the blob
        """
        return self.blob_id_file_dict.get(blob_sha)

    def get_branch_form_a_commit(self, commit_sha):
        """

        :param commit_sha: hashid of a commit object
        :return: branch name associated with the commit
        """
        return self.commit_branch_dict.get(commit_sha)

    def get_all_remote_branch_list(self):
        """

        :return: all remote branches available as a list
        """
        return self.branch_list

    def form_all_info_for_a_blob_sha(self, blob_sha, time_zone=None):
        """

        :param blob_sha: hashid of a blob object
        :param time_zone: in the remote repo, the timezone may be different
        from your local time zone, give your timezone. (default None).
        :return: a dict of all necessary info
        """
        blob_info = dict()
        all_commit_ids = self.get_commits_for_a_blob(blob_sha)
        if all_commit_ids is None:
            logger.warning("Unable to find commit ids, probably git gc had "
                           "not been run yet for blob_id %s", blob_sha)
            return None
        first_commit_id = all_commit_ids[len(all_commit_ids) - 1]
        commit_info = self.find_info_for_a_commit_id(first_commit_id)
        blob_info['first_commit_sha'] = first_commit_id
        blob_info['file_name'] = self.get_file_name_for_blob_id(blob_sha)
        blob_info['branch'] = self.get_branch_form_a_commit(
            first_commit_id)
        if not blob_info['branch']:
            blob_info['branch'] = "Error in getting branch info :( "
            blob_info['other_info'] = "It has been merged"
        blob_info['branch_name'] = blob_info['branch'].split('/')[-1]
        blob_info['author_name'] = commit_info.author
        blob_info['author_email'] = commit_info.email
        blob_info['first_commit_subject'] = commit_info.subject
        blob_info['unix_time_stamp'] = commit_info.timestamp
        blob_info['size_in_kb'] = round(int(self.blob_size_in_bytes[
                                                blob_sha]) / float(1024), 2)
        blob_info['size_in_mb'] = round(int(self.blob_size_in_bytes[
                                                blob_sha]) / float(
            (1024 * 1024)), 2)
        blob_info['commit_time'] = datetime.fromtimestamp(
            int(blob_info['unix_time_stamp']), time_zone).strftime(
            '%Y-%m-%d %H:%M:%S')
        # blob_info['all_commit_ids'] = all_commit_ids

        return blob_info

    def get_blob_ids_greater_than_given_size(self):
        """

        :return: blobids greater than the given threshold size
        """
        return self.get_blob_ids_from_pack_file()

    def print_file_with_info(self):
        """

        :return: prints all information in the console
        """
        list_of_tuple = self.get_blob_ids_greater_than_given_size()
        for entry in list_of_tuple:
            logger.info(self.form_all_info_for_a_blob_sha(entry[0]))

    def _get_all_file_with_info(self):
        list_of_fat_checkins = list()
        list_of_tuple = self.get_blob_ids_greater_than_given_size()
        for entry in list_of_tuple:
            all_info = self.form_all_info_for_a_blob_sha(entry[0])
            if all_info:
                list_of_fat_checkins.append(self.form_all_info_for_a_blob_sha(
                    entry[0]))
        return list_of_fat_checkins

    def get_dormant_branch_info(self):
        """

        :return: a sorted list containing :py:class:`ExtraCommitInfo` object.
        The list
        contains all branches available.
        """
        branch_last_commit_info_list = list()
        branch_list = self.get_all_remote_branch_list()
        for branch in branch_list:
            commit_list = self.get_commit_list_for_a_branch(branch)
            if len(commit_list) == 0:
                logger.warning("Not checking branch %s, probably merged",
                               branch)
                continue
            first_commit_id = commit_list[len(commit_list) - 1]
            last_commit_id = commit_list[0]
            first_commit_info = self.find_info_for_a_commit_id(first_commit_id)
            last_commit_info = self.find_info_for_a_commit_id(last_commit_id)
            diff_time = time.time() - int(last_commit_info.timestamp)
            branch_last_commit_info_list.append(ExtraCommitInfo(
                last_commit_info, diff_time, branch, first_commit_info))

        sorted_list = sorted(branch_last_commit_info_list)
        return sorted_list

    def domant_branch_info(self, threshold_val=4320000):
        """

        :param threshold_val: the value beyond which the branch is
        considered as dormant. It is given in seconds. (default 4320000)
        which is 50 days.
        :return: a list of dictionary with branch information above the given threshold value.
        """
        list_of_branches_with_info = list()
        exta_commit_info_objs = self.get_dormant_branch_info()
        for extra_commit_info in exta_commit_info_objs:
            commit_info_dict = dict()
            full_branch_name = extra_commit_info.branch_name
            commit_info_dict['full_branch_name'] = full_branch_name
            commit_info_dict['branch'] = full_branch_name.split('/')[-1]
            commit_info_dict['last_commit_time'] = \
                extra_commit_info.last_commit_obj.timestamp
            commit_info_dict['author_name'] = \
                extra_commit_info.last_commit_obj.author
            commit_info_dict['author_email'] = \
                extra_commit_info.last_commit_obj.email
            commit_info_dict['last_commit_subject'] = \
                extra_commit_info.last_commit_obj.subject
            commit_info_dict['difference_time'] = extra_commit_info.diff_time
            commit_info_dict['last_commit_h_time'] = datetime.fromtimestamp(
                int(
                    extra_commit_info.last_commit_obj.timestamp)).strftime(
                '%Y-%m-%d')
            if extra_commit_info.diff_time - threshold_val > 0:
                list_of_branches_with_info.append(commit_info_dict)

        return list_of_branches_with_info
