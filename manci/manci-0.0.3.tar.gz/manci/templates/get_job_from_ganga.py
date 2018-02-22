from collections import Counter
import json

j_id = {{j_id}}
output_fn = '{{output_fn}}'

if j_id in jobs.ids():
    lfns = []
    job_statuses = Counter()
    for sj in jobs(j_id).subjobs:
        job_statuses[sj.status] += 1
        if sj.status == 'completed':
            assert len(sj.outputfiles) == 1
            assert isinstance(sj.outputfiles[0], DiracFile)
            lfns.append(sj.outputfiles[0].lfn)

    result = {
        'lfns': lfns,
        'job_statuses': job_statuses,
    }
else:
    result = {
        'error': 'Invalid job ID: '+str(j_id)
    }


with open(output_fn, 'wt') as fp:
    json.dump(result, fp)
