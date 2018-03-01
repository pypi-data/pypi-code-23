import json
import shlex
import subprocess
import os
import re
from jira import JIRA


def get_jira():
    with open("{home}/.jira".format(home=os.getenv("HOME"))) as config:
        return JIRA(**json.loads(config.read()))


def get_opened_issues(jira):
    return {
        str(issue): issue
        for issue in jira.search_issues("assignee = currentUser() and  status = 'In Progress'")
    }


def get_current_branch():
    branch = subprocess.check_output(shlex.split("git rev-parse --abbrev-ref HEAD"))
    return branch.strip().decode("utf-8")


def get_gtm_total_time():
    return parse_time(subprocess.check_output(shlex.split("gtm status -total-only")).strip())


def commit_time_by_gtm():
    subprocess.check_output(shlex.split("gtm commit --yes"))


def parse_time(total_only):
    total_only = total_only.decode("utf-8")
    (new_string, number_of_subs_made) = re.subn(
        r'([a-zA-Z])', r'\1 ', total_only.strip()
    )
    return " ".join(new_string.split(" ")[:-2]).strip()


def parse_issue_key(branch_name):
    matched_result = re.match(r'^([A-Z]+-[0-9]+)', branch_name)
    return matched_result[0] if matched_result else None


if __name__ == "__main__":
    branch = get_current_branch()
    issue_key = parse_issue_key(branch)
    time_spent = get_gtm_total_time()

    jira = get_jira()
    opened_issues = get_opened_issues(jira)

    print("-- Time logger --")
    print("Your current branch is: ", get_current_branch())
    print("Your issue key is: ", issue_key)
    print("Your time spend: ", time_spent)

    if issue_key in opened_issues:
        issue = opened_issues[issue_key]
        if time_spent:
            try:
                commit_time_by_gtm()
                jira.add_worklog(issue, timeSpent=time_spent, comment="")
                print("Time successfully logged, thanks!")
            except subprocess.CalledProcessError:
                print("time already checked in last commit, please make one more commit...")
        else:
            print("Unfortunetly i cant see if you  spent any time for this task :(\n")
    else:
        print("***************************************")
        print("No tickets opened for this issue found\n")
