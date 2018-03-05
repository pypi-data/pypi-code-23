from co.logup.clients.APIClient import APIClient


class Subscription:

    def __init__(self, api_client, id_subscription, id_actor=None, db=None):
        """
        Create an instance of Subscription class

        :type api_client: APIClient
        :param api_client: API client previously created

        :type id_subscription: str
        :param id_subscription: Id subscription

        :type id_actor: str
        :param id_actor: Id actor related to this subscription

        :type db: dict
        :param db: Db values associated to this subscription
        """
        self._api_client = api_client
        self._id_subscription = id_subscription
        self._id_actor = id_actor
        self._db = db
        self._is_new_user = None

    @property
    def db(self):
        # type: () -> dict
        """
        Get db values associated to the subscription stored

        :rtype: dict
        :return: All db values stored

        :raise RuntimeError: API call failed
        :raise ValueError: There's no subscription selected to ask for DB
        """
        if self._id_subscription is None:
            raise ValueError("No subscription selected to ask for DB")
        if not self.db_stored() is None:
            return self.db_stored()
        response = self._api_client.get("/subscription/" + self._id_subscription + "/db")
        if APIClient.can_proceed(response):
            self._db = response.json()
            return self.db_stored()
        error = response.json()["errorMessage"]
        if error is None:
            error = response.json()["error"]
        raise RuntimeError("Failed : HTTP error code : " + str(response.status_code) + " and error " + error)

    def db_stored(self):
        # type: () -> dict
        """
        Get db values stored

        :rtype: dict
        :return: DB values stored
        """
        return self._db

    def delete_db_value(self, keys):
        # type: (list) -> dict
        """

        :type keys: list
        :param keys: List of keys to be deleted from the db values

        :rtype: dict
        :return: Db values updated

        :raise RuntimeError: API call failed
        :raise ValueError: There's no subscription selected to ask for DB
        """
        if self._id_subscription is None:
            raise ValueError("No subscription selected to ask for DB")
        fields = {"keys": keys}
        response = self._api_client.delete("/subscription/" + self._id_subscription + "/db", fields)
        if APIClient.can_proceed(response):
            self._db = None
            return self.db
        error = response.json()["errorMessage"]
        if error is None:
            error = response.json()["error"]
        raise RuntimeError("Failed : HTTP error code : " + str(response.status_code) + " and error " + error)

    @property
    def id_actor(self):
        # type: () -> str
        """
        Get id actor

        :rtype str
        :return: Id actor
        """
        return self._id_actor

    @property
    def id_subscription(self):
        # type: () -> str
        """
        Get id subscription

        :rtype: str
        :return: Id subscription
        """
        return self._id_subscription

    @id_subscription.setter
    def id_subscription(self, id_subscription):
        """
        Set id subscription

        :type id_subscription: str
        :param id_subscription: Id subscription to be set
        """
        self._id_subscription = id_subscription

    @property
    def is_new_user(self):
        # type: () -> bool
        """
        Get if the user is a new user for your website or not.

        :rtype: bool
        :return: True if it's a new user for your website, false otherwise.
        """
        return self._is_new_user

    @is_new_user.setter
    def is_new_user(self, is_new_user):
        """
        Set if it's the user is a new user for your website or not

        :type is_new_user: bool
        :param is_new_user: True if it's a new user for your website, false otherwise
        """
        self._is_new_user = is_new_user

    def update_db(self, data):
        # type: (dict) -> dict
        """
        Update db values associated to the subscription

        :type data: dict
        :param data: Key-Value dictionary containing all values to be updated

        :rtype: dict
        :return: All db values associated to the subscription loaded (including the db values updated)

        :raise RuntimeError: API call failed
        :raise ValueError: There's no subscription selected to ask for DB
        """
        if self._id_subscription is None:
            raise ValueError("No subscription selected to ask for DB")
        internal_data = []
        for key, value in data.iteritems():
            internal_data.append({
                    "key": key,
                    "value": value
            }.copy())
        fields = {"data": internal_data}
        print(fields)
        response = self._api_client.put("/subscription/" + self._id_subscription + "/db", fields);
        if APIClient.can_proceed(response):
            self._db = response.json()
            return self.db_stored()
        error = response.json()["errorMessage"]
        if error is None:
            error = response.json()["error"]
        raise RuntimeError("Failed : HTTP error code : " + str(response.status_code) + " and error " + error)
