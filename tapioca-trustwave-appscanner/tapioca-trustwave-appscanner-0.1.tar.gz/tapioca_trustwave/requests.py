from tapioca.exceptions import ServerError

from tapioca_trustwave import Trustwave

api = Trustwave()


def request_application_id_by_name(application_name, ):
    try:
        request = api.get_application_id_by_name(application_name=application_name).get()
        return request().data
    except ServerError as e:
        raise e
