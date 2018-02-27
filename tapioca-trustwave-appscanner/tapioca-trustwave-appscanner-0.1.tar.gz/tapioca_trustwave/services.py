from tapioca.exceptions import ClientError

from tapioca_trustwave.requests import request_application_id_by_name


def get_application_id_by_name(application_name: str):
    if len(application_name) > 60:
        raise ClientError('O nome da aplicação deve conter no máximo 60 caracteres')

    if ' ' in application_name:
        raise ClientError('O nome da aplicação não pode conter espaços em branco')

    application_data = request_application_id_by_name(application_name)
    application_id = application_data.get('application-id')

    return application_id
