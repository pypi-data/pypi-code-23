from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class BioService(Request, OnyxErpService):
    """
    Serviço responsável pela interação de APIs do OnyxERP com a BiometriaAPI
    """
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(BioService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "SocialAPI")

    def inserir_bio(self):
        """
        Cadastra os registros biométricos de digital de uma pessoa física na BiometriaAPI
        """
        response = self.post("/v2/bio/")

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False
