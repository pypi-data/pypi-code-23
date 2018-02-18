from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class SmsService(Request, OnyxErpService):
    """
    SmsService
    """
    jwt = None
    cache_path = str()

    def __init__(self, base_url: str(), app: object(), cache_root="/tmp/"):
        super(SmsService, self).__init__(app, base_url)
        self.cache_path = cache_root

    def enviar_sms(self, pf_id: str(), telefone: str(), mensagem: str(), remetente="OnyxERP"):
        """
        Envia uma requisição de envio de sms para a SmsAPI
        :rtype: dict | bool
        """
        request = self.set_payload({
            'remetente': remetente,
            'telefone': telefone,
            'mensagem': mensagem,
        }).post("/v2/enviar/%s/" % pf_id)

        status = request.get_status_code()

        if status == 200:
            return True
        else:
            return False
