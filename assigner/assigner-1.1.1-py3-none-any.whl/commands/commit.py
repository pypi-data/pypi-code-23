import logging
import os

from requests.exceptions import HTTPError
from git.exc import NoSuchPathError

from assigner.roster_util import get_filtered_roster
from assigner.baserepo import RepoError, StudentRepo
from assigner.config import config_context
from assigner.progress import Progress

help = "Push changes to student repos"

logger = logging.getLogger(__name__)


@config_context
def push(conf, args):
    hw_name = args.name
    hw_path = args.path
    host = conf.gitlab_host
    namespace = conf.namespace
    token = conf.gitlab_token
    semester = conf.semester
    branch = args.branch
    force = args.force
    push_unlocked = args.push_unlocked

    path = os.path.join(hw_path, hw_name)

    roster = get_filtered_roster(conf.roster, args.section, args.student)

    progress = Progress()

    for student in progress.iterate(roster):
        username = student["username"]
        student_section = student["section"]
        full_name = StudentRepo.build_name(semester, student_section,
                                           hw_name, username)

        try:
            repo = StudentRepo(host, namespace, full_name, token)
            repo_dir = os.path.join(path, username)
            repo.add_local_copy(repo_dir)

# If committing:
    # Default: git add -u (equivalent to passing -a to git commit)
    # Optional: pass args to git add
    # Commit with given message
            # TODO custom branches
            index = repo.repo.index

            # TODO optional commit
            if True:
                # TODO select which files to add
                # Stage modified and deleted files for commit
                for change in index.diff(None):
                    if change.deleted_file:
                        logging.debug("%s: git rm %s", full_name, change.b_path)
                        index.remove([change.b_path])
                    else:
                        logging.debug("%s: git add %s", full_name, change.b_path)
                        index.add([change.b_path])

                # TODO message, author?
                index.commit("asdf")

        except NoSuchPathError:
            logging.warning("Local repo for %s does not exist; skipping...", username)
        except RepoError as e:
            logging.warning(e)
        except HTTPError as e:
            if e.response.status_code == 404:
                logging.warning("Repository %s does not exist.", full_name)
            else:
                raise

    progress.finish()

def setup_parser(parser):
    parser.add_argument("name",
                        help="Name of the assignment to commit to.")
    parser.add_argument("path", default=".", nargs="?",
                        help="Path of student repositories to commit to")
    parser.add_argument("--branch", nargs="?", default="master",
                        help="Local branch to commit to")
    parser.add_argument("-a", "--add", nargs="+", dest="add", default=[],
                        help="Files to add before committing")
    parser.add_argument("-d", "--delete", nargs="+", dest="delete", default=[],
                        help="Files to delete before committing")
    parser.add_argument("--section", nargs="?",
                        help="Section to commit to")
    parser.add_argument("--student", metavar="id",
                        help="ID of student whose assignment is to be committed to.")
    parser.set_defaults(run=push)
