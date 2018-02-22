from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
from os.path import basename
import sys

from .structures import Replica
from .utils import grouper


__all__ = [
    'lookup_files_from_query',
    'loookup_replicas',
    'mirror_files',
]


def lookup_files_from_query(bk_path):
    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bkQuery = BKQuery(bkQuery=bk_path, visible='Yes')
    bkClient = BookkeepingClient()

    files = {}
    useFilesWithMetadata = False
    if useFilesWithMetadata:
        res = bkClient.getFilesWithMetadata(bkQuery.getQueryDict())
        if not res['OK']:
            print('ERROR getting the files', res['Message'], file=sys.stderr)
            sys.exit(1)
        parameters = res['Value']['ParameterNames']
        for record in res['Value']['Records']:
            dd = dict(zip(parameters, record))
            lfn = dd.pop('FileName')
            files[lfn] = dd

    else:
        lfns = bkQuery.getLFNs(printSEUsage=False, printOutput=False)

        for lfnChunk in grouper(lfns, 1000):
            res = bkClient.getFileMetadata(lfnChunk)
            if not res['OK']:
                print('ERROR: failed to get metadata:', res['Message'], file=sys.stderr)
                sys.exit(1)
            files.update(res['Value']['Successful'])

    if not files:
        print('No files found for BK query')
        sys.exit(0)

    print(len(files), 'files found')

    return files


def loookup_replicas(files, protocol=['xroot', 'root']):
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    from DIRAC.Resources.Storage.StorageElement import StorageElement
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    dm = DataManager()
    bk = BookkeepingClient()

    res = dm.getReplicas(list(files), getUrl=False)
    replicas = res.get('Value', {}).get('Successful', {})
    seList = sorted(set(se for lfn in files for se in replicas.get(lfn, {})))
    banned_SE_list = [se for se in seList if 'CNAF' in se]
    print('Found SE list of', seList)

    for lfn in files:
        files[lfn]['Replicas'] = []

    # Check if files are MDF
    bkRes = bk.getFileTypeVersion(list(files))
    assert not set(lfn for lfn, fileType in bkRes.get('Value', {}).iteritems() if fileType == 'MDF')
    for se in seList:
        # TODO Check if SEs are available
        lfns = [lfn for lfn in files if se in replicas.get(lfn, [])]

        if se in banned_SE_list:
            print('Skipping banned SE', se)
            for lfn in lfns:
                files[lfn]['Replicas'].append(Replica(lfn, se, banned=True))
            continue
        else:
            print('Looking up replicas for', len(lfns), 'files at', se)

        if lfns:
            res = StorageElement(se).getURL(lfns, protocol=protocol)
            if res['OK']:
                for lfn, pfn in res['Value']['Successful'].items():
                    files[lfn]['Replicas'].append(Replica(lfn, se, pfn=pfn))
                for lfn in res['Value']['Failed']:
                    files[lfn]['Replicas'].append(Replica(lfn, se, error=res))
            else:
                print('LFN -> PFN lookup failed for', se, 'with error:', res['Message'])
                for lfn in lfns:
                    files[lfn]['Replicas'].append(Replica(lfn, se, error=res['Message']))


def mirror_files(files, destination_dir, max_retries=1):
    from urban_barnacle import XRootD

    assert destination_dir.startswith('root://'), destination_dir
    assert len(files) == len(set(basename(lfn) for lfn in files)), 'Duplicate filenames found in input LFNs'

    n_tries = defaultdict(int)
    destination_dir = XRootD.URL(destination_dir)

    # Validate checksums of existing files
    for lfn, metadata in files.items():
        destination = destination_dir.join(basename(lfn))
        if destination.exists:
            validated = False
            for replica in metadata['Replicas']:
                if replica.available:
                    destination.validate_checksum(replica.pfn)
                    validated = True
                    break
            if not validated:
                print('Failed to validate checksum for', lfn, 'as no replicas are available')

    # Copy files which don't exist, repeating as needed
    keep_going = True
    while keep_going:
        copy_process = XRootD.CopyProcess()
        for lfn, metadata in files.items():
            destination = destination_dir.join(basename(lfn))
            if not destination.exists:
                for replica in metadata['Replicas']:
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
    for lfn, metadata in files.items():
        destination = destination_dir.join(basename(lfn))
        if destination.exists:
            n_successful += 1
        else:
            n_failed += 1
            print('Failed to copy', lfn, 'replicas are:')
            for replica in metadata['Replicas']:
                print(' >', replica)
            print()
    print(n_successful, 'out of', len(files), 'files copied successfully')
