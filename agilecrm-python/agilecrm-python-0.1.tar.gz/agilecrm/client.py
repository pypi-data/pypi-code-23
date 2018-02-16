import requests
from agilecrm.exceptions import UnauthorizedError, WrongFormatInputError, ContactsLimitExceededError


class Client(object):
    BASE_URL = 'https://{}.agilecrm.com/dev/api/'

    def __init__(self, api_key, email, domain):
        self.api_key = api_key
        self.email = email
        self.domain = domain
        self.url = self.BASE_URL.format(self.domain)

    def create_contact(self, data):
        """Accepts contact JSON as post data along with the credentials of domain User (User name and API Key).

        Each field is case sensitive.
        Please don't pass null value.
        If you don't know value of field then either don't pass that field or pass empty data to a field.

        Args:
            data: A dict with the contact's data.

        Returns:
            A dict.

        """
        return self._post('contacts', data=data)

    def get_contacts(self, params=None):
        """Returns list of contacts in domain which are ordered by creation time.

        Args:
            params : Paging can be applied using the page_size and cursor query parameters

        Returns:
            A dict.

        """
        return self._get('contacts/', params=params)

    def get_contact_by_id(self, contact_id):
        """Returns contact object which is associated with given id

        Args:
            contact_id: A string with the contact's id.

        Returns:
            A dict.

        """
        return self._get('contacts/{}'.format(contact_id))

    def get_contact_by_email(self, email):
        """Returns contact object which is associated with given email

        Args:
            email: A string with the contact's email.

        Returns:
            A dict.

        """
        return self._get('contacts/search/email/{}'.format(email))

    def update_contact(self, data):
        """We can update required property fields of the contact using this call.
        It is used to add the new property or update the existing property.
        It accepts property object of contact with valid parameter in it.
        We need to send the Contact-Id of the contact to identify it.
        This will not affect other fields.

        Using this API you can not delete properties.
        If subtype is same for phone,website or email then value can be overridden.
        Lead score, star value and tags can not be updated using this API.
        follow the below API for editing lead score,star value and tags.

        Args:
            data: A dict with the contact's data.

        Returns:

        """
        return self._put('contacts/edit-properties', data=data)

    def delete_contact(self, contact_id):
        """Deletes contact based on the id of the contact, which is sent in request url path.

        Args:
            contact_id: A string with the contact's id.

        Returns:

        """
        return self._delete('contacts/{}'.format(contact_id))

    def search_contact(self, data):
        """Returns contacts or companies object which is associated with given filter

        Args:
            data: A dict with the query.

        Returns:
            A dict.

        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self._post('filters/filter/dynamic-filter', data=data, headers=headers, json=False)

    def create_deal(self, data):
        """Accepts deal JSON as data in Post request to the url specified above,
        which creates new deal and returns the deal JSON with id field generated when new deal is created.
        If Post data includes valid deal id, respective deal is updated with the data sent in request.
        Milestone name should be same as the the one in the website and it is case sensitive.
        (If the milestone name is given in the wrong case, it will not be shown in the milestone view.)

        Each field is case sensitive.

        Please don't pass null value.

        If you don't know value of field then either don't pass that field or pass empty data to a field.

        Note : expected_value is mandatory field.

        Args:
            data: A dict with the deal's data.

        Returns:
            A dict.

        """
        return self._post('opportunity', data=data)

    def get_deal_by_id(self, deal_id):
        """Gets the deal with the given ID.

        Args:
            deal_id: A string with the deal's id.

        Returns:
            A dict.

        """
        return self._get('opportunity/{}'.format(deal_id))

    def update_deal(self, data):
        """We can update deal using this call. It accepts Deal JSON.
        Id parameter of the deal should be specified. It indicates the deal to be updated with the new data sent.
        Milestone name should be same as the the one in the website and it is case sensitive.
        (If the milestone name is given in wrong case, it will not be shown in the milestone view.).
        This will not affect other fields.

        Args:
            data: A dict with the deal's data.

        Returns:

        """
        return self._put('opportunity/partial-update', data=data)

    def delete_deal(self, deal_id):
        """Deletes the deal based on the id specified in the url.

        Args:
            deal_id: A string with the deal's id.

        Returns:

        """
        return self._delete('opportunity/{}'.format(deal_id))

    def create_contact_note(self, data):
        """Creates a note and relates it to contacts, which are sent in the note JSON contact field.

        Args:
            data: A dict with the note's data.

        Returns:
            A dict.

        """
        return self._post('notes', data=data)

    def get_note_by_contact_id(self, contact_id):
        """Returns list of note JSONs related to the contact.

        Args:
            contact_id: A string with the contact's id.

        Returns:
            A dict.

        """
        return self._get('contacts/{}/notes'.format(contact_id))

    def delete_contact_note(self, contact_id, note_id):
        """Deletes the note of the specific contact. (It will remove the relationship between the note and the contact.)

        Args:
            contact_id: A string with the contact's id.
            note_id: A string with the note's id.

        Returns:

        """
        return self._delete('contacts/{}/notes/{}'.format(contact_id, note_id))

    def create_deal_note(self, data):
        """Accepts note JSON as data in Post request to the url specified above, which creates new note
        and returns the note JSON with id field generated when new note is created.

        Args:
            data: A dict with the note's data.

        Returns:
            A dict.

        """
        return self._post('opportunity/deals/notes', data=data)

    def get_note_by_deal_id(self, deal_id):
        """Gets the deal with the given ID.

        Args:
            deal_id: A string with the deal's id.

        Returns:
            A dict.

        """
        return self._get('opportunity/{}/notes'.format(deal_id))

    def update_deal_note(self, data):
        """Accepts note JSON as data in Post request to the url specified above,
        which update note and returns the deal JSON with id field generated when new note is created.

        Args:
            data: A dict with the note's data.

        Returns:

        """
        return self._put('opportunity/deals/notes', data=data)

    def delete_deal_note(self, data):
        """Deletes notes of the specific deal.

        Args:
            data:

        Returns:

        """
        return self._post('contacts/notes/bulk', data=data)

    def create_event(self, data):
        """Creates an event.

        Args:
            data: A dict with the event's data.

        Returns:
            A dict.

        """
        return self._post('events', data=data)

    def get_event_by_contact_id(self, contact_id):
        """Gets the deal with the given ID.

        Args:
            contact_id: A string with the contact's id.

        Returns:
            A dict.

        """
        return self._get('contacts/{}/events/sort'.format(contact_id))

    def update_event(self, data):
        """Updates an event. To update the event, the event id has to be provided in the request object.
        Otherwise, it will be considered as a new event.

        Args:
            data: A dict with the event's data.

        Returns:

        """
        return self._put('events', data=data)

    def delete_event(self, event_id):
        """Deletes the event with the particular id. The id passed in the url will be used to identify the event.

        Args:
            event_id:

        Returns:

        """
        return self._post('events/{}'.format(event_id))

    def create_task(self, data):
        """Creates a new task.
        - Acceptable value for below field :
         progress (0 to 100), is_complete (true or false), type (CALL, EMAIL, FOLLOW_UP, MEETING, MILESTONE, SEND, TWEET, OTHER),
         priority_type (HIGH, NORMAL, LOW), status (YET_TO_START, IN_PROGRESS, COMPLETED)

        Args:
            data: A dict with the task's data.

        Returns:
            A dict.

        """
        return self._post('tasks', data=data)

    def get_task_by_id(self, task_id):
        """Gets the task of the contact with the given ID.

        Args:
            task_id: A string with the task's id.

        Returns:
            A dict.

        """
        return self._get('tasks/{}'.format(task_id))

    def update_task(self, data):
        """We can update task using this call. It accepts task JSON. Id parameter of the task should be specified.
        This will not affect other fields.

        Args:
            data: A dict with the task's data.

        Returns:

        """
        return self._put('tasks/partial-update', data=data)

    def delete_task(self, task_id):
        """Deletes the task having the given ID.

        Args:
            task_id: A string with the task's id.

        Returns:

        """
        return self._delete('tasks/{}'.format(task_id))

    def search_task(self, params):
        """Retrives the list of tasks based on the given filters.
        The filters available are ‘type’, ‘owner’, ’pending’, ‘criteria’, and ‘page_size’.
        These should be sent as a query parameters in the URL.
        - There are three criteria can be use using this api and each has its own type.
        - criteria = CATEGORY has these type (EMAIL,CALL,FOLLOW_UP,MEETING,MILESTONE,SEND,TWEET,OTHER)
        - criteria = STATUS has these type (IN_PROGRESS,YET_TO_START,COMPLETED)
        - criteria = PRIORITY has these type (HIGH,NORMAL,LOW)

        Paging can be applied using the page_size and cursor query parameters. Count of the tasks will be in the first task and Cursor for the next page will be in the last task of the list. If there is no cursor, it means that it is the end of list.

        Args:
            params: A dict with the query.

        Returns:
            A dict.

        """
        return self._get('tasks/based', params=params)

    def _get(self, endpoint, params=None):
        response = self._request('GET', endpoint, params=params)
        return self._parse(response)

    def _post(self, endpoint, params=None, data=None, headers=None, json=True):
        response = self._request('POST', endpoint, params=params, data=data, headers=headers, json=json)
        return self._parse(response)

    def _put(self, endpoint, params=None, data=None):
        response = self._request('PUT', endpoint, params=params, data=data)
        return self._parse(response)

    def _delete(self, endpoint, params=None):
        response = self._request('DELETE', endpoint, params=params)
        return self._parse(response)

    def _request(self, method, endpoint, params=None, data=None, headers=None, json=True):
        _headers = self._headers()
        if headers:
            _headers.update(headers)
        kwargs = {}
        if json:
            kwargs['json'] = data
        else:
            kwargs['data'] = data
        return requests.request(method, self.url + endpoint, params=params, headers=_headers,
                                auth=(self.email, self.api_key), **kwargs)

    def _parse(self, response):
        status_code = response.status_code
        if 'application/json' in response.headers['Content-Type']:
            r = response.json()
        else:
            r = response.text
        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 406:
            raise ContactsLimitExceededError(r)
        if status_code == 500:
            raise Exception
        return r

    def _headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
