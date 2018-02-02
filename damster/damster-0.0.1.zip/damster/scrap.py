#!/bin/env python
from damster.utils import initialize_logger, get_config
from atlassian import Bamboo
from pprint import pprint

log = initialize_logger(__name__)


cfg = get_config()
result = {
    'deploymentVersion': {
        'id': 1343490,
        'name': 'release-2.2',
        'creationDate': 1517490874517,
        'creatorUserName': 'admin',
        'items': [{
            'id': 1409026,
            'name': 'dummy_artifact',
            'planResultKey': {'key': 'SPEC-SP1-2',
                              'entityKey': {'key': 'SPEC-SP1'},
                              'resultNumber': 2},
            'type': 'BAM_ARTIFACT',
            'label': 'dummy_artifact',
            'location': '',
            'copyPattern': 'artifact.txt',
            'size': 44,
            'artifact': {
                'id': 1114114,
                'label': 'dummy_artifact',
                'size': 44,
                'isSharedArtifact': True,
                'isGloballyStored': False,
                'linkType': 'com.atlassian.bamboo.plugin.artifact.handler.local:ServerLocalArtifactHandler'
                    ,
                'planResultKey': {'key': 'SPEC-SP1-2',
                                  'entityKey': {'key': 'SPEC-SP1'},
                                  'resultNumber': 2},
                'archiverType': 'NONE',
                },
            }],
        'operations': {
            'canView': True,
            'canEdit': True,
            'canDelete': True,
            'allowedToExecute': False,
            'canExecute': False,
            'allowedToCreateVersion': True,
            'allowedToSetVersionStatus': True,
            },
        'creatorDisplayName': 'Admin',
        'creatorGravatarUrl': 'https://secure.gravatar.com/avatar/7ed7b765d3b83b8e5fd8059fd3843d1e.jpg?r=g&s=24&d=mm',
        'planBranchName': 'master',
        'ageZeroPoint': 1517490881513,
        },
    'deploymentVersionName': 'release-2.2',
    'id': 1474564,
    'deploymentState': 'SUCCESS',
    'lifeCycleState': 'FINISHED',
    'startedDate': 1517490881511,
    'queuedDate': 1517490881523,
    'executedDate': 1517490881567,
    'finishedDate': 1517490881611,
    'reasonSummary': 'Manual run by <a href="http://bamboo.xabarin.com/browse/user/admin">Admin</a>',
    'key': {'key': '1179649-1277953-1474564',
            'entityKey': {'key': '1179649-1277953'},
            'resultNumber': 1474564},
    'agent': {
        'id': 196609,
        'name': 'Default Agent',
        'type': 'LOCAL',
        'active': True,
        'enabled': True,
        'busy': False,
        },
    'operations': {
        'canView': True,
        'canEdit': True,
        'canDelete': True,
        'allowedToExecute': True,
        'canExecute': True,
        'allowedToCreateVersion': False,
        'allowedToSetVersionStatus': False,
        },
    }

build_result = {
    'artifacts': {'max-result': 1, 'size': 1, 'start-index': 0},
    'buildCompletedDate': '2018-02-01T13:14:05.744Z',
    'buildCompletedTime': '2018-02-01T13:14:05.744Z',
    'buildDuration': 235,
    'buildDurationDescription': '< 1 second',
    'buildDurationInSeconds': 0,
    'buildNumber': 2,
    'buildReason': 'Manual run by <a '
                'href="http://bamboo.xabarin.com/browse/user/admin">Admin</a>',
    'buildRelativeTime': '1 day ago',
    'buildResultKey': 'SPEC-SP1-2',
    'buildStartedTime': '2018-02-01T13:14:05.509Z',
    'buildState': 'Successful',
    'buildTestSummary': 'No tests found',
    'changes': {'max-result': 0, 'size': 0, 'start-index': 0},
    'comments': {'max-result': 0, 'size': 0, 'start-index': 0},
    'continuable': False,
    'expand': 'changes,metadata,plan,artifacts,comments,labels,jiraIssues,stages',
    'failedTestCount': 0,
    'finished': True,
    'id': 1048579,
    'jiraIssues': {'max-result': 0, 'size': 0, 'start-index': 0},
    'key': 'SPEC-SP1-2',
    'labels': {'max-result': 0, 'size': 0, 'start-index': 0},
    'lifeCycleState': 'Finished',
    'link': {'href': 'http://localhost:8085/rest/api/latest/result/SPEC-SP1-2',
          'rel': 'self'},
    'metadata': {'max-result': 3, 'size': 3, 'start-index': 0},
    'notRunYet': False,
    'number': 2,
    'onceOff': False,
    'plan': {'enabled': True,
          'key': 'SPEC-SP1',
          'link': {'href': 'http://localhost:8085/rest/api/latest/plan/SPEC-SP1',
                   'rel': 'self'},
          'name': 'Specs - SP1',
          'planKey': {'key': 'SPEC-SP1'},
          'shortKey': 'SP1',
          'shortName': 'SP1',
          'type': 'chain'},
    'planName': 'SP1',
    'planResultKey': {'entityKey': {'key': 'SPEC-SP1'},
                   'key': 'SPEC-SP1-2',
                   'resultNumber': 2},
    'prettyBuildCompletedTime': 'Thu, 1 Feb, 01:14 PM',
    'prettyBuildStartedTime': 'Thu, 1 Feb, 01:14 PM',
    'projectName': 'Specs',
    'quarantinedTestCount': 0,
    'reasonSummary': 'Manual run by <a '
                  'href="http://bamboo.xabarin.com/browse/user/admin">Admin</a>',
    'restartable': False,
    'skippedTestCount': 0,
    'stages': {'max-result': 1, 'size': 1, 'start-index': 0},
    'state': 'Successful',
    'successful': True,
    'successfulTestCount': 0
                }

bamboo = Bamboo(**cfg['Bamboo'])


for artifact in result['deploymentVersion']['items']:
    log.info('Getting info for plan: {}'.format(artifact))
    plan_key = artifact['planResultKey']['key']
    build = bamboo.results(plan_key, expand=None)
    pprint(build)
