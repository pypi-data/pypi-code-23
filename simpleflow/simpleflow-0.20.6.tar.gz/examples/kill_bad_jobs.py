#!/usr/bin/env python
import os
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

from swf.exceptions import ResponseError
from swf.models import Domain
from swf.querysets import WorkflowExecutionQuerySet

SWF_DOMAIN = "com.botify.saas.production.backend"

domain = Domain(SWF_DOMAIN)
qs = WorkflowExecutionQuerySet(domain)
executions = qs.filter(tag="type=website_validation")

for exe in executions:
    if exe.workflow_type.name != "job":
        continue
    if "user=iprospectfr" not in exe.tag_list:
        continue
    print exe.workflow_id, exe.start_timestamp, exe.tag_list
    try:
        exe.terminate()
    except ResponseError:
        print "oops, couldn't terminate this job. Already finished?"
