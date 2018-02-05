
from . import _VDAPIService, _VDAPIResponse, _VDAPISingleResponse

class _DomainListResponse(_VDAPISingleResponse):
    """
    Override to give you access to the actual domains
    """

    def get_domains(self, **kwargs):
        """
        Get the list of domains that are in this domain list

            d = springserve.domain_list.get(id)
            domains = d.get_domains()

            for domain in domains:
                print domain.name

        """
        return self._service.get("{}/domains".format(self.id), **kwargs)
    
    def _to_list(self, input_list):
        """
        The api needs a list, and you can't serialize sets, or Series
        """
        if isinstance(input_list, list):
            return input_list

        return [x for x in input_list]

    def add_domains(self, domains):
        """
        Add a list of domains to this domain list

            d = springserve.domain_list.get(id)
            d.add_domains(['blah.com', 'blah2.com'])

        domains: List of domains you would like to add 
        """
        payload = {'names':self._to_list(domains)}
        resp = self._service.post(payload,
                                  path_param='{}/domains/bulk_create'.format(self.id)
                                 )
        return resp

    def remove_domains(self, domains):
        """
        Add a list of domains to this domain list

            d = springserve.domain_list.get(id)
            d.remove_domains(['blah.com', 'blah2.com'])

        domains: List of domains you would like to add 
        """
        payload = {'names':self._to_list(domains)}
        resp = self._service.bulk_delete(payload,
                                  path_param='{}/domains/bulk_delete'.format(self.id)
                                 )
        return resp



class _DomainListAPI(_VDAPIService):

    __API__ = "domain_lists"
    __RESPONSE_OBJECT__ = _DomainListResponse


class _BillItemAPI(_VDAPIService):

    __API__ = "bill_items"

    def __init__(self, bill_id):
        super(_BillItemAPI, self).__init__()
        self.bill_id = bill_id

    @property
    def endpoint(self):
        """
        The api endpoint that is used for this service.  For example:: 
            
            In [1]: import springserve

            In [2]: springserve.supply_tags.endpoint
            Out[2]: '/supply_tags'

        """
        return "/bills/{}/bill_items".format(self.bill_id)


class _BillResponse(_VDAPISingleResponse):
    
    def get_bill_items(self):
        # Need to make a new one per bill
        return _BillItemAPI(self.id).get()

    def _add_bill_item(self, data, **kwargs):
        return _BillItemAPI(self.id).post(data, **kwargs)


class _BillAPI(_VDAPIService):

    __API__ = "bills"
    __RESPONSE_OBJECT__ = _BillResponse

class _ValueAPI(_VDAPIService):

    __API__ = "values"

    def __init__(self, key):
        super(_ValueAPI, self).__init__()
        self.key_id = key.id
        self.account_id = key.account_id 

    @property
    def endpoint(self):
       return "/keys/{}/values".format(self.key_id)


class _KeyResponse(_VDAPISingleResponse):

    def get_values(self):
        return _ValueAPI(self).get()

    def add_value(self, data, **kwargs):
        return _ValueAPI(self).post(data, **kwargs)
 
class _KeyAPI(_VDAPIService):

    __API__ = "keys"
    __RESPONSE_OBJECT__ = _KeyResponse

