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

            if repo.is_locked() or push_unlocked:
                info = repo.repo.remote().push(branch, force=force, set_upstream=True)
                for line in info:
                    logging.debug("%s: flags: %s, branch: %s, summary: %s", full_name, line.flags, line.local_ref, line.summary)
                    if line.flags & line.ERROR:
                        logging.warning("%s: push to %s failed: %s", full_name, line.local_ref, line.summary)
            else:
                logging.warning("%s: repo is not locked (run 'assigner lock %s' first)", full_name, hw_name)

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
                        help="Name of the assignment to push.")
    parser.add_argument("path", default=".", nargs="?",
                        help="Path to push student repositories from")
    parser.add_argument("--branch", "--branches", nargs="+", default=["master"],
                        help="Local branch or branches to push")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force-push student repositories")
    parser.add_argument("-u", "--push-unlocked", action="store_true", dest="push_unlocked",
                        help="Push to student repos even if they are unlocked")
    parser.add_argument("--section", nargs="?",
                        help="Section to push")
    parser.add_argument("--student", metavar="id",
                        help="ID of student whose assignment needs pushing.")
    parser.set_defaults(run=push)
