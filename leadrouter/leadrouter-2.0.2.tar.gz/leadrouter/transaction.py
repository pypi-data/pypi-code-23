from itertools import chain

class Transaction(object):
    '''
    Transaction wraps a Client 
    '''

    def __init__(self, client):
        self.client = client
        self.actions = []

    def begin(self):
        self.actions = []

    def commit(self):
        for call in self._combine(self.actions):
            method = getattr(self.client, call['method'])
            method(**call['params'])
        self.actions = []

    def _combine(self, actions):
        leads = {}

        KEEP_IN_LIST = True       # return value to keep an action into 'actions'
        REMOVE_FROM_LIST = False  # return value to remove an action from 'actions'

        def extract_leads(action):
            '''
            Filter function to remove from 'actions' all actions of type 'create_lead'
            and put into 'leads' dictionary
            '''
            if action['method'] != 'create_lead':
                return KEEP_IN_LIST
            if 'id' not in action['params']['lead']:
                return KEEP_IN_LIST
            lead_key = '%s/%s' % (action['params']['site_uuid'],
                                  action['params']['lead']['id'])
            leads[lead_key] = action
            return REMOVE_FROM_LIST

        def merge_activities_into_lead(action):
            '''
            Filter function to remove action from 'actions' if it's an activity that
            belongs to one of the leads in 'leads' dict
            '''
            if action['method'] != 'add_activities':
                return KEEP_IN_LIST
            lead_key = '%s/%s' % (action['params']['site_uuid'],
                                  action['params']['lead_uuid'])
            lead = leads.get(lead_key)
            if not lead:
                return KEEP_IN_LIST
            lead['params']['lead'].setdefault('activities', [])
            lead['params']['lead']['activities'].extend(action['params']['activities'])
            return REMOVE_FROM_LIST

        actions = filter(extract_leads, actions)
        actions = filter(merge_activities_into_lead, actions)

        return chain(leads.values(), actions)

    def create_lead(self, site_uuid, lead):
        self.actions.append({
            'method': 'create_lead',
            'params': {
                'site_uuid': site_uuid,
                'lead': lead,
            }
        })

    def update_lead(self, site_uuid, lead_uuid, lead):
        self.actions.append({
            'method': 'update_lead',
            'params': {
                'site_uuid': site_uuid,
                'lead_uuid': lead_uuid,
                'lead': lead,
            }
        })

    def add_activities(self, site_uuid, lead_uuid, activities):
        self.actions.append({
            'method': 'add_activities',
            'params': {
                'site_uuid': site_uuid,
                'lead_uuid': lead_uuid,
                'activities': activities,
            }
        })

    def create_potential_seller_lead(self, site_uuid, lead):
        self.actions.append({
            'method': 'create_potential_seller_lead',
            'params': {
                'site_uuid': site_uuid,
                'lead': lead,
            }
        })
