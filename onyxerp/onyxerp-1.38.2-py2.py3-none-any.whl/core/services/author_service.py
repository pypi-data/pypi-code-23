"""
author_service
"""
import datetime
from collections import OrderedDict

from onyxerp.core.services.base_service import BaseService
from onyxerp.core.services.social_service_v2 import SocialServiceV2


class AuthorService(BaseService):
    """
    AuthorService
    """

    app = object
    cache_service = object
    url_social = str
    cache_path = str

    def __init__(self, app: object, url_social: str(), cache_path: str()):
        super(AuthorService, self).__init__(app)
        self.app = app
        self.url_social = url_social
        self.cache_path = cache_path

    def get_author_info(self, uupfid: str, author_oid: str, data_hora: datetime) -> OrderedDict:
        """
        Busca as informações de uma pessoa física em SocialAPI e retorna no formato de author
        :param uupfid: str
        :param author_oid: str
        :param data_hora: datetime
        :rtype OrderedDict
        """
        author_pf_info = self.load_social_service().get_pf_perfil(uupfid)

        retorno = OrderedDict()
        retorno['oid'] = author_oid
        retorno['uupfid'] = uupfid
        retorno['nome'] = author_pf_info['pf_nome'] if author_pf_info else None
        retorno['foto_url'] = self.get_author_pf_foto(author_pf_info['files'], author_oid) if author_pf_info else None
        retorno['timestamp'] = int(data_hora.timestamp()) if type(data_hora) == datetime.datetime else None

        return retorno

    def get_author_pf_foto(self, files: OrderedDict, author_oid: str):
        """
        Busca uma foto(pública ou privada se for do mesmo OID) nos arquivos da pessoa física retornada pelo end-point
        GET v1/pessoa-fisica/perfil/{pf_id}/ em SocialAPI
        :param files: OrderedDict Objeto files retornado no GET do perfil
        :param author_oid: str Id do órgão do Author
        :return str | None
        """
        jwt_data = self.get_jwt_data()
        fotos = files['wa9tia']
        # Possui ao menos uma foto pública?
        if len(fotos['public']) > 0:
            return fotos['public'][0]['foto_url']
        else:
            # Possui ao menos uma foto privada?
            if len(fotos['private']) > 0:
                # O author é do mesmo órgão de quem está listando?
                if jwt_data['user']['oid'] == author_oid:
                    return fotos['private'][0]['foto_url']

        return None

    def load_social_service(self) -> SocialServiceV2:
        """
        Load SocialServiceV2
        :return: SocialServiceV2
        """
        return SocialServiceV2(self.url_social, self.app, self.cache_path)\
            .set_jwt(self.get_jwt()).\
            set_payload(self.get_payload())
