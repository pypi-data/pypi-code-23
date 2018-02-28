from tapioca_trustwave.requests import request_application_id_by_name, request_assessment_id_by_name, \
    request_assessment_status
from tapioca_trustwave.validators import is_valide_uuid4, is_valid_application_name


def get_application_id_by_name(application_name):
    is_valid_application_name(application_name)

    application_data = request_application_id_by_name(application_name)
    application_id = application_data.get('application-id')

    return application_id


def get_assessment_id_by_name(application_id, assessment_name):
    is_valide_uuid4(application_id)

    assessment_data = request_assessment_id_by_name(application_id, assessment_name)
    assessment_id = assessment_data.get('assessment-id')

    return assessment_id


def get_assessment_status(application_id, assessment_id):
    is_valide_uuid4(application_id)
    is_valide_uuid4(assessment_id)

    assessment_data = request_assessment_status(application_id, assessment_id)
    status = assessment_data.get('assessment-status')

    return status
