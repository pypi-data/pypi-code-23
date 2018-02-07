from jobs import *
import subprocess
from collections import Counter

user = subprocess.check_output("whoami").strip()

job_list = fetch_jobs(user=user,local=True)

# print job_list
# print len(job_list)

master_jobs = [ job['status'] for job in job_list if job['group'] == 'master']
sub_jobs = [ job['status'] for job in job_list if job['group'] == 'subjob']

# print master_jobs
# print len(master_jobs)

# print sub_jobs
# print len(sub_jobs)

master_counts = Counter(master_jobs)
sub_counts = Counter(sub_jobs)

# print master_counts
# print sub_counts

# dic_master = dict(sub_counts)
# print dic_master

get_status(user,local=True)
