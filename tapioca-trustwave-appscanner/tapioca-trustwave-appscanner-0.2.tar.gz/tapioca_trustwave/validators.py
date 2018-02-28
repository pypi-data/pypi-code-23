from uuid import UUID

from tapioca.exceptions import ClientError

max_application_name = 60


def is_valide_uuid4(uuid_string):
    """
    Verifica se a uuid é válida
    """

    try:
        UUID(uuid_string, version=4)
    except ValueError:
        raise ClientError('parameter must be in uuid4 format')


def is_valid_application_name(application_name):
    if len(application_name) > max_application_name:
        raise ClientError(
            'The application name must contain a maximum of {} characters'.format(str(max_application_name)))
