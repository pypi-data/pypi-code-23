


from octo_drf.settings import project_settings

from octo_drf.apps.metadata.models import MetaData
from octo_drf.apps.base_siteconfig.models import Config

from octo_drf.apps.metadata.views import MetaDataViewSet
from octo_drf.apps.base_siteconfig.views import ConfigViewSet

"""
CACHE_MAP - это словарь служащий для инвалидации кеша
Ключи - db_table модели, полученный из клас метода get_map_key()
Значения - список вью, в которых участвует данная модель.
При каждом сохранении модели, все ключи в redis в которых есть
название вью из списка, удаляются
"""
meta_key = MetaData.get_map_key()
config_key = Config.get_map_key()

CACHE_MAP = {
    meta_key: [MetaDataViewSet],
    config_key: [ConfigViewSet]
}

user_map = project_settings['caching']['map']
if user_map:
    CACHE_MAP.update(user_map)
