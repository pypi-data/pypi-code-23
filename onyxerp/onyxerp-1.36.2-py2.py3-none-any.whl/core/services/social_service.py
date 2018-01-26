from collections import OrderedDict

from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class SocialService(Request, OnyxErpService):
    """
    SocialService
    """
    jwt = None
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(SocialService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "SocialAPI")

    def get_pessoa_fisica(self, pf_cod: int()):
        """

        :param pf_cod:
        :return:
        """
        cached_data = self.cache_service.get_cached_data('pf', pf_cod)

        if cached_data:
            return cached_data

        response = self.get("/v1/pessoa-fisica/{0}/".format(pf_cod))

        status = response.get_status_code()

        if status == 200:
            data = response.get_decoded()['data']
            self.cache_service.write_cache_data('pf', pf_cod, data)
            return data
        else:
            return {
                "status": status,
                "response": response.get_content()
            }

    def get_info_account(self, pf_id: str()):
        """

        :param pf_id:
        :return:
        """
        cached_data = self.cache_service.get_cached_data('info-account', pf_id)

        if cached_data:
            return cached_data

        response = self.get("/v1/pessoa-fisica/info-account/{0}/".format(pf_id))

        status = response.get_status_code()

        if status == 200:
            data = response.get_decoded()['data']
            self.cache_service.write_cache_data('info-account', pf_id, data)
            return data
        else:
            return {
                "status": status,
                "response": response.get_content()
            }

    def get_pessoa_juridica(self, pj_cod: int()):

        """

        :param pj_cod:
        :return:
        """
        response = self.get("/v1/pessoa-juridica/%s/" % pj_cod)

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            if type(dados['data']) == OrderedDict:
                return dados['data']

        return {
            "status": status,
            "response": response.get_content()
        }

    def get_pessoa_juridica_by_id(self, pj_id: int()):
        """

        :param pj_id:
        :return:
        """
        response = self.get("/v2/pessoa-juridica/{0}/".format(pj_id))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            if type(dados['data']) == OrderedDict:
                return dados['data']

        return {
            "status": status,
            "response": response.get_content()
        }

    def inserir_pessoa_juridica(self):
        """

        :return:
        """
        response = self.post("/v2/pessoa-juridica/")

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            if type(dados['data']) == OrderedDict:
                return dados['data']

        return {
            "status": status,
            "response": response.get_content()
        }

    def alterar_pessoa_juridica(self, pj_id: str):
        """

        :param pj_id:
        :return:
        """
        response = self.put("/v2/pessoa-juridica/{0}/".format(pj_id))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            if type(dados['data']) == OrderedDict:
                return dados['data']

        return {
            "status": status,
            "response": response.get_content()
        }

    def get_pf_cod_by_id(self, pf_id: str):
        """

        :param pf_id:
        :return:
        """
        cached_data = self.cache_service.get_cached_data('pf-id-cod', pf_id)

        if cached_data:
            return cached_data['pf_cod']

        response = self.get("/v1/pf/cod/{0}/".format(pf_id))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            if type(dados['data']) == OrderedDict:
                return dados['data']

        return {
            "status": status,
            "response": response.get_content()
        }
