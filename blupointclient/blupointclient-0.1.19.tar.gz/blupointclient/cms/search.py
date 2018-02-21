import asyncio
import slugify
from flasky import errors
from blupointclient.cms import components_base
from quark_utilities import temporal_helpers



class BlupointCmsSearch(components_base):

    def __init__(self, settings):
        super(BlupointCmsSearch, self).__init__(settings)
        self.settings = settings

    async def query(self, q, **kwargs):
        params = self.prepare_query(kwargs, ignore=['sort'])
        self.set_token(kwargs.get("token", None))

        url = self.prepare_delivery_endpoint('simple-search',
                                             q = q,
                                             select = params.get("select"),
                                             types = params.get("types"),
                                             paths = params.get("paths"),
                                             skip = params.get("skip"),
                                             limit = params.get("limit"),
                                             sort = params.get("sort") )

        search_result = await self._get(url, api='delivery')

        items = search_result['data']['items']
        count = search_result['data']['count']

        return items, count

