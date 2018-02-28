import asyncio
from blupointclient.cms import components_base

class BlupointCmsContents(components_base):

    def __init__(self, settings):
        super(BlupointCmsContents, self).__init__(settings)
        self.settings = settings

    async def get(self, **kwargs):
        params = self.prepare_query(kwargs)
        filters = {}
        self.update_filters(filters, params['document'])
        self.set_token(kwargs.get("token", None))

        """
        # will be used for get_user_contents later
        self.update_filters(params['document'], {
            'panel_access.' + str(params['user']['_id']) + '.permissions': "read"
        })
        """

        url = self.prepare_endpoint("contents", "_query",
                                    skip=params.get("skip"),
                                    limit=params.get("limit"),
                                    sort=params.get("sort"))

        tasks = []
        items = []
        count = 0
        if params.get('all_content', 'false') == 'true':
            response = await self._post(url, filters)

            while params['skip'] < response['data']['count']:
                url = self.prepare_endpoint("contents", "_query",
                                            skip=params.get("skip"),
                                            limit=params.get("limit"),
                                            sort=params.get("sort"))

                tasks.append(self._post(url, params['document']))

                params['skip'] += params['limit']

            results = await asyncio.gather(*tasks)

            for result_item in results:
                items += result_item['data']['items']
                count += len(result_item['data']['items'])

        else:
            response = await self._post(url, filters)
            items = response['data']['items']
            count = response['data']['count']

        relation_tasks = []

        for item in items:
            relation_tasks.append(self.expand_content_field(item))
        await asyncio.gather(*relation_tasks)

        return items, count