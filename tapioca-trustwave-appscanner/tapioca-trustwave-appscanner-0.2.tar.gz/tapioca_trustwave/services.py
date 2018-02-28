from tapioca_trustwave.requests import request_application_id_by_name, request_assessment_id_by_name
from tapioca_trustwave.validators import is_valide_uuid4, is_valid_application_name


def get_application_id_by_name(application_name):
    is_valid_application_name(application_name)

    application_data = request_application_id_by_name(application_name)
    application_id = application_data.get('application-id')

    return application_id


def get_assessment_id_by_name(application_id, assessment_name):
    is_valide_uuid4(application_id)

    application_data = request_assessment_id_by_name(application_id, assessment_name)
    application_id = application_data.get('application-id')

    return application_id
