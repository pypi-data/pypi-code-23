from uuid import UUID

from tapioca.exceptions import ClientError

max_application_name = 60


def validate_uuid4(uuid_string):
    """
    Verifica se a uuid é válida
    """

    try:
        UUID(uuid_string, version=4)
    except ValueError:
        raise ClientError('parameter must be in uuid4 format')


def validate_application_name(application_name):
    if len(application_name) > max_application_name:
        raise ClientError(
            'The application name must contain a maximum of {} characters'.format(str(max_application_name)))
