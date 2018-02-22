from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class SocialServiceV2(Request, OnyxErpService):
    """
    Serviço responsável pela interação de APIs do OnyxERP com a SocialAPI-v2
    """
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(SocialServiceV2, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "SocialAPI")

    def inserir_pf(self):
        """
        Cadastra uma pessoa física em SocialAPI, informando apenas o CPF, recuperando demais dados através da integração
        com a Serasa Experian®
        """
        response = self.post("/v2/pessoa-fisica/inserir/")

        status = response.get_status_code()

        if status == 201:
            dados = response.get_decoded()
            return dados['data']['SocialAPI']
        else:
            return False

    def inserir_pf_v3(self):
        """
        Cadastra uma pessoa física em SocialAPI, informando o CPF e a data de nascimento, recuperando demais dados
        através da integração com a Serasa Experian®
        """
        response = self.post("/v3/pessoa-fisica/inserir/")

        status = response.get_status_code()

        if status == 201:
            dados = response.get_decoded()
            return dados['data']['SocialAPI']
        else:
            return False

    def inserir_pf_foto(self, pf_id: str) -> bool:
        """
        Cadastra uma foto para uma pessoa física em SocialAPI
        :param pf_id: str
        :rtype bool
        """
        response = self.post("/v1/pessoa-fisica/foto/%s/" % pf_id)

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def inserir_pf_tel(self) -> bool:
        """
        Cadastra um telefone para uma pessoa física em SocialAPI
        :rtype bool
        """
        response = self.post("/v1/pessoa-fisica/telefones/")

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def inserir_pf_email(self) -> bool:
        """
        Cadastra um email para uma pessoa física em SocialAPI
        :rtype bool
        """
        response = self.post("/v1/pessoa-fisica/emails/")

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def document_change(self) -> bool:
        """
        Vincula um file_id a um tipo de documento da pessoa física em SocialAPI
        :rtype bool
        """
        response = self.put("/v1/pessoa-fisica/document/change/")

        status = response.get_status_code()

        if status == 200:
            return True
        else:
            return False

    def registra_foto_perfil(self) -> bool:
        """
        Registra um file_id como foto do perfil da Pessoa Física em SocialAPI
        :rtype bool
        """
        response = self.post("/v1/pessoa-fisica/foto/")

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def get_pf_perfil(self, pf_id: str()):
        """
        Busca uma pessoa física pela id em SocialAPI
        :param pf_id: str
        :return: dict | False
        """
        cached_data = self.cache_service.get_cached_data('pessoa', pf_id)
        if cached_data:
            return cached_data

        response = self.get("/v1/pessoa-fisica/perfil/%s/" % str(pf_id))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            pf_data = dados['data']['SocialAPI']

            self.cache_service.write_cache_data('pessoa', pf_id, pf_data)

            return pf_data
        else:
            return False

    def get_pf_telefones(self, pf_id: str()):
        """
        Lista os telefones de uma pessoa física pela id em SocialAPI
        :param pf_id: str
        :return: dict | False
        """
        response = self.get("/v1/pessoa-fisica/telefones/%s/" % str(pf_id))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            pf_data = dados['data']['SocialAPI']['current']

            return pf_data
        else:
            return False

    def get_pf_tel_tipo(self, pf_id: str, tipo: str)-> list or False:
        """
        Lista os telefones de uma pessoa física pela id em SocialAPI, filtrando apenas os que batem com o tipo informado
        podendo set 'M'(Móvel) ou 'F'(Fixo).
        :param pf_id: str
        :param tipo: str
        :return: list | False
        """
        telefones = self.get_pf_telefones(pf_id)

        if telefones is False:
            return False

        telefones_tipo = list()
        for telefone in telefones:
            if telefone['tel_tipo'] == tipo:
                telefones_tipo.append(telefone)

        return telefones_tipo if len(telefones_tipo) > 0 else False

    def get_search_pf(self, cpf: str()):
        """
        Busca uma pessoa física pelo CPF em SocialAPI
        :param cpf: str
        :return: dict | False
        """
        cached_data = self.cache_service.get_cached_data('pf_id_cpf', cpf)
        if cached_data:
            return self.get_pf_perfil(cached_data)

        response = self.get("/v1/pessoa-fisica/search/%s/" % str(cpf))

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            pf_data = dados['data']['SocialAPI']

            pf_id = pf_data['pf_id']
            self.cache_service.write_cache_data('pf_id_cpf', cpf, pf_data['pf_id'])

            # Atualiza os dados do get_perfl, pois os retornos são idênticos
            self.cache_service.write_cache_data('pessoa', pf_id, pf_data)

            return pf_data
        else:
            return False

    def get_search_cpf_pf_id(self, cpf: str()) -> dict or False:
        """
        Busca uma pessoa física pelo CPF em SocialAPI, retornando apenas o pf_id, se encontrado...
        :param cpf: str
        :return: dict | False
        """
        cached_data = self.cache_service.get_cached_data('pf_id_cpf', cpf)
        if cached_data:
            return cached_data
        search = self.get_search_pf(cpf)
        if search:
            return search['pf_id']
        else:
            return False

    def social_exchange(self) -> list or False:
        """
        Acessa o end-point de social data exchange em SocialAPI
        :return: list or False
        """
        response = self.post("/v1/pessoa-fisica/exchange/")

        status = response.get_status_code()

        if status == 200:
            dados = response.get_decoded()
            pf_data = dados['data']['SocialAPI']
            return pf_data
        else:
            return False
