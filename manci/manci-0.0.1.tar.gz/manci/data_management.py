from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
from os.path import basename

from .structures import Replica


__all__ = [
    'loookup_replicas',
    'mirror_files',
]


def loookup_replicas(files, protocol=['xroot', 'root']):
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    from DIRAC.Resources.Storage.StorageElement import StorageElement
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    dm = DataManager()
    bk = BookkeepingClient()

    files_map = {f.lfn: f for f in files}

    res = dm.getReplicas([f.lfn for f in files], getUrl=False)
    replicas = res.get('Value', {}).get('Successful', {})
    seList = sorted(set(se for f in files for se in replicas.get(f.lfn, {})))
    banned_SE_list = [se for se in seList if 'CNAF' in se]
    print('Found SE list of', seList)

    # Check if files are MDF
    bkRes = bk.getFileTypeVersion([f.lfn for f in files])
    assert not set(lfn for lfn, fileType in bkRes.get('Value', {}).iteritems() if fileType == 'MDF')
    for se in seList:
        # TODO Check if SEs are available
        lfns = [f.lfn for f in files if se in replicas.get(f.lfn, [])]

        if se in banned_SE_list:
            print('Skipping banned SE', se)
            for lfn in lfns:
                files_map[lfn].replicas.append(Replica(lfn, se, banned=True))
            continue
        else:
            print('Looking up replicas for', len(lfns), 'files at', se)

        if lfns:
            res = StorageElement(se).getURL(lfns, protocol=protocol)
            if res['OK']:
                for lfn, pfn in res['Value']['Successful'].items():
                    files_map[lfn].replicas.append(Replica(lfn, se, pfn=pfn))
                for lfn in res['Value']['Failed']:
                    files_map[lfn].replicas.append(Replica(lfn, se, error=res))
            else:
                print('LFN -> PFN lookup failed for', se, 'with error:', res['Message'])
                for lfn in lfns:
                    files_map[lfn].replicas.append(Replica(lfn, se, error=res['Message']))


def mirror_files(files, destination_dir, max_retries=1):
    from manci import XRootD

    assert destination_dir.startswith('root://'), destination_dir
    assert len(files) == len(set(basename(f.lfn) for f in files)), 'Duplicate filenames found in input LFNs'

    n_tries = defaultdict(int)
    destination_dir = XRootD.URL(destination_dir)

    # Validate checksums of existing files
    for file in files:
        destination = destination_dir.join(basename(file.lfn))
        if destination.exists:
            validated = False
            for replica in file.replicas:
                if replica.available:
                    destination.validate_checksum(replica.pfn)
                    validated = True
                    break
            if not validated:
                print('Failed to validate checksum for', file.lfn, 'as no replicas are available')

    # Copy files which don't exist, repeating as needed
    keep_going = True
    while keep_going:
        copy_process = XRootD.CopyProcess()
        for file in files:
            destination = destination_dir.join(basename(file.lfn))
            if not destination.exists:
                for replica in file.replicas:
                    if not replica.available:
                        continue
                    if n_tries[replica] <= max_retries:
                        copy_process.add_job(replica, destination)
                        n_tries[replica] += 1
                        break

        copy_result = copy_process.copy()
        for replica, success in copy_result.items():
            destination = destination_dir.join(basename(replica.lfn))
            if success:
                destination.validate_checksum(replica.pfn)
            else:
                assert not destination.exists, (replica, destination)
        keep_going = copy_process and not all(copy_result.values())

    # Print the results
    n_successful = 0
    n_failed = 0
    for file in files:
        destination = destination_dir.join(basename(file.lfn))
        if destination.exists:
            n_successful += 1
        else:
            n_failed += 1
            print('Failed to copy', file.lfn, 'replicas are:')
            for replica in file.replicas:
                print(' >', replica)
            print()
    print(n_successful, 'out of', len(files), 'files copied successfully')
