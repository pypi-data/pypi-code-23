from tapioca_trustwave import Trustwave

from .validators import validate_uuid4, validate_application_name

api = Trustwave()


def application_exists(application_id):
    validate_uuid4(application_id)

    request = api.get_application_id_by_name(application_id).get()
    application_data = request().data

    application_exists = application_data.get('application-exists')
    return application_exists


def get_application_id_by_name(application_name):
    validate_application_name(application_name)

    request = api.get_application_id_by_name(application_name).get()
    application_data = request().data

    application_id = application_data.get('application-id')
    return application_id


def assessment_exists(application_id, assessment_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    request = api.check_if_assessment_exists(application_id, assessment_id).get()
    assessment_data = request().data

    assessment_exists = assessment_data.get('assessment-exists')
    return assessment_exists


def get_assessment_id_by_name(application_id, assessment_name):
    validate_uuid4(application_id)

    request = api.get_assessment_id_by_name(application_id, assessment_name).get()
    assessment_data = request().data

    assessment_id = assessment_data.get('assessment-id')
    return assessment_id


def get_assessment_status(application_id, assessment_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    request = api.get_assessment_status(application_id, assessment_id).get()
    assessment_data = request().data

    status = assessment_data.get('assessment-status')
    return status


def get_current_assessment_run_id(application_id, assessment_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    request = api.get_assessment_runs(application_id, assessment_id).get()
    assessment_data = request().data

    status = assessment_data.get('assessment-status')
    return status


def get_assessment_run_status(application_id, assessment_run_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_run_id)

    request = api.get_assessment_runs(application_id, assessment_run_id).get()
    assessment_data = request().data

    status = assessment_data.get('assessment-status')

    return status


def get_assessment_run_results(application_id, assessment_run_id):
    validate_uuid4(application_id)
    validate_uuid4(assessment_run_id)

    request = api.get_assessment_runs(application_id, assessment_run_id).get()
    assessment_data = request().data

    status = assessment_data.get('assessment-status')
    return status


def queue_assessment(application_id, assessment_id, test_only=False):
    validate_uuid4(application_id)
    validate_uuid4(assessment_id)

    params = {
        'test-only': test_only
    }

    request = api.queue_assessment(application_id, assessment_id).put(data=params)
    assessment_data = request().data

    status = assessment_data.get('status-code')
    return status
