from __future__ import absolute_import, division, print_function, unicode_literals

from collections import Iterable
import json
import logging

from amaascore.assets.utils import json_to_asset
from amaascore.core.interface import Interface
from amaascore.core.amaas_model import json_handler


class AssetsInterface(Interface):

    def __init__(self, environment=None, endpoint=None, logger=None, username=None,
                       password=None, session_token=None):
        self.logger = logger or logging.getLogger(__name__)
        super(AssetsInterface, self).__init__(endpoint=endpoint, endpoint_type='assets', session_token=session_token,
                                              environment=environment, username=username, password=password)

    def new(self, asset):
        self.logger.info('New Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s' % (self.endpoint, asset.asset_manager_id)
        response = self.session.post(url, json=asset.to_interface())
        if response.ok:
            self.logger.info('Successfully Created Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def create_many(self, assets):
        if not assets or not isinstance(assets, list):
            raise ValueError('Invalid argument. Argument must be a non-empty list.')

        self.logger.info('New Assets - Asset Manager: %s', assets[0].asset_manager_id)
        url = '%s/assets/%s' % (self.endpoint, assets[0].asset_manager_id)
        json_body = [asset.to_interface() for asset in assets]
        response = self.session.post(url, json=json_body)
        if response.ok:
            self.logger.info('Successfully Created Assets - Asset Manager: %s', assets[0].asset_manager_id)
            assets = [asset for asset in response.json()]
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def upsert(self, asset):
        ''' upsert only support upserting one asset at a time'''
        self.logger.info('Upsert Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s' % (self.endpoint, asset.asset_manager_id)
        response = self.session.post(url, json=asset.to_interface(), params={'upsert': True})
        if response.ok:
            self.logger.info('Successfully Upserted Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()


    def amend(self, asset):
        self.logger.info('Amend Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id, asset.asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset.asset_manager_id, asset.asset_id)
        response = self.session.put(url, json=asset.to_interface())
        if response.ok:
            self.logger.info('Successfully Amended Asset - Asset Manager: %s - Asset ID: %s', asset.asset_manager_id,
                             asset.asset_id)
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def partial(self, asset_manager_id, asset_id, updates):
        self.logger.info('Partial Amend Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                         asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        # Setting handler ourselves so we can be sure Decimals work
        response = self.session.patch(url, data=json.dumps(updates, default=json_handler), headers=self.json_header)
        if response.ok:
            asset = json_to_asset(response.json())
            return asset
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, asset_id, version=None):
        self.logger.info('Retrieve Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id, asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        if version:
            url += '?version=%d' % int(version)
        response = self.session.get(url)
        if response.ok:
            self.logger.info('Successfully Retrieved Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                             asset_id)
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def deactivate(self, asset_manager_id, asset_id):
        self.logger.info('Deactivate Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id, asset_id)
        url = '%s/assets/%s/%s' % (self.endpoint, asset_manager_id, asset_id)
        json = {'asset_status': 'Inactive'}
        response = self.session.patch(url, json=json)
        if response.ok:
            self.logger.info('Successfully Deactivated Asset - Asset Manager: %s - Asset ID: %s', asset_manager_id,
                             asset_id)
            return json_to_asset(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def loose_search(self, asset_manager_id, query='', **kwargs):
        """
        Asset search API.

        Possible kwargs:
           * threshold: int (default = 0)
           * page_no: int (default = 1)
           * page_size: int (default = 100)
           * sort_fields: list (default = [])
           * asset_types: list (default = [])
           * include_public: bool (default = True)
           * include_data_sources: bool (default = True)
        """
        self.logger.info('Asset Search - Asset Manager: %s', asset_manager_id)
        url = '{endpoint}/assets/search/{asset_manager_id}'.format(
            asset_manager_id=asset_manager_id,
            endpoint=self.endpoint,
        )
        params = {'query': query}
        for k, v in kwargs.items():
            if not isinstance(v, str) and isinstance(v, Iterable):
                v = ','.join(str(i) for i in v)

            params[k] = v

        response = self.session.get(url, params=params)
        if response.ok:
            data = response.json()
            assets = [json_to_asset(json_asset) for json_asset in data.get('hits', [])]
            self.logger.info('Returned %s Assets.', len(assets))
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_id, **kwargs):
        """
            Search for assets.

            Possible kwargs:
             * client_ids: list[int]
             * asset_statuses: list
             * asset_ids: list
             * reference_types: list
             * reference_values: list
             * asset_issuer_ids: list[int]
             * asset_classes: list
             * asset_types: list
             * country_ids: list
             * currencies: list

             * include_public: bool (default = True)
             * include_data_sources: bool (default = True)

             * page_no = int(query_params.get('page_no', '1')) if query_params else None
             * page_size = int(query_params.get('page_size', '100')) if query_params else None

        """
        self.logger.info('Search for Assets - Asset Manager: %s', asset_manager_id)
        search_params = {}
        for k, v in kwargs.items():
            if not isinstance(v, str) and isinstance(v, Iterable):
                v = ','.join(str(i) for i in v)

            search_params[k] = v

        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            self.logger.info('Returned %s Assets.', len(assets))
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def fields_search(self, asset_manager_id, asset_ids=None,
                      asset_classes=None, asset_types=None,
                      fields=None, page_no=None, page_size=None):
        self.logger.info('Search for Assets - Asset Manager: %s', asset_manager_id)
        search_params = {}

        if asset_ids:
            search_params['asset_ids'] = ','.join(asset_ids)
        if asset_classes:
            search_params['asset_classes'] = ','.join(asset_classes)
        if asset_types:
            search_params['asset_types'] = ','.join(asset_types)
        if fields:
            search_params['fields'] = ','.join(fields)
        if page_no is not None:
            search_params['page_no'] = page_no
        if page_size:
            search_params['page_size'] = page_size

        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url, params=search_params)
        if response.ok:
            asset_dicts = response.json()
            self.logger.info('Returned %s Assets.', len(asset_dicts))
            return asset_dicts
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def assets_by_asset_manager(self, asset_manager_id):
        self.logger.info('Retrieve Assets By Asset Manager: %s', asset_manager_id)
        url = '%s/assets/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            assets = [json_to_asset(json_asset) for json_asset in response.json()]
            self.logger.info('Returned %s Assets.', len(assets))
            return assets
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def assets_lifecycle(self, asset_manager_id, business_date, asset_ids):
        self.logger.info('Retrieve Assets Lifecycle. Asset Manager: %s', asset_manager_id)
        url = '%s/asset-lifecycle/%s' % (self.endpoint, asset_manager_id)
        params = {'business_date': business_date.isoformat(),
                  'asset_ids': ','.join(asset_ids)}
        response = self.session.get(url, params=params)
        if response.ok:
            asset_lifecycles = response.json()
            self.logger.info('Returned %s Asset Lifecycles.', len(asset_lifecycles))
            return asset_lifecycles
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def clear(self, asset_manager_id):
        """ This method deletes all the data for an asset_manager_id.
            It should be used with extreme caution.  In production it
            is almost always better to Inactivate rather than delete. """
        self.logger.info('Clear Assets - Asset Manager: %s', asset_manager_id)
        url = '%s/clear/%s' % (self.endpoint, asset_manager_id)
        response = self.session.delete(url)
        if response.ok:
            count = response.json().get('count', 'Unknown')
            self.logger.info('Deleted %s Assets.', count)
            return count
        else:
            self.logger.error(response.text)
            response.raise_for_status()
