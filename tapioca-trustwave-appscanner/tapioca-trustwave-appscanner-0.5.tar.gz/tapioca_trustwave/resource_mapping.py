# coding: utf-8

RESOURCE_MAPPING = {
    'check_if_application_exists': {
        'resource': '/application/{application_id}/exists',
        'methods': ['GET']
    },
    'create_application': {
        'resource': '/application',
        'methods': ['POST']
    },
    'get_application_id_by_name': {
        'resource': '/application/{application_name}/id',
        'methods': ['GET']
    },
    'get_assessments_by_app_id': {
        'resource': '/application/{application_id}/assessments',
        'methods': ['GET']
    },
    'get_assessment_id_by_name': {
        'resource': '/application/{application_id}/assessment/{assessment_name}/id',
        'methods': ['GET']
    },
    'get_assessment_runs': {
        'resource': '/application/{application_id}/assessment/{assessment_id}/runs',
        'methods': ['GET']
    },
    'get_assessment_run_results': {
        'resource': '/application/{application_id}/assessmentrun/{assessment_run_id}/results?getRequestResponseData=true&includePagesVisited=true&onlyDistinctPagesVisited=true&exportFormat=json',
        'methods': ['GET']
    },
    'get_assessment_run_status': {
        'resource': '/application/{application_id}/assessmentrun/{assessment_run_id}/status',
        'methods': ['GET']
    },
    'create_assessment': {
        'resource': '/application/{application_id}/assessment',
        'methods': ['POST']
    },
    'queue_assessment': {
        'resource': '/application/{application_id}/assessment/{assessment_id}/queue',
        'methods': ['PUT']
    },
    'get_assessment_status': {
        'resource': '/application/{application_id}/assessment/{assessment_id}/status',
        'methods': ['GET']
    },
    'check_if_assessment_exists': {
        'resource': '/application/{application_id}/assessment/{assessment_id}/exists',
        'methods': ['GET']
    },
}
