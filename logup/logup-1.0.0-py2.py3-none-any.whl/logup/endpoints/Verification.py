from co.logup.clients.APIClient import APIClient
from co.logup.endpoints.Subscription import Subscription


class Verification:

    def __init__(self, api_client):
        """
        Create an instance of Verification class.

        :type api_client: APIClient
        :param api_client: API client previously created
        """
        self._api_client = api_client
        self._subscription = None

    @property
    def subscription(self):
        # type: () -> Subscription
        """
        Get subscription authenticated

        :rtype: Subscription
        :return: Subscription authenticated
        """
        return self._subscription

    def verify_user(self, logup_token):
        # type: (str) -> bool
        """
        Verify the logup token received.

        :type logup_token: str
        :param logup_token: Logup token to be verified

        :rtype: bool
        :return: True if the user is verified, false otherwise.
        """
        fields = {"logupToken": logup_token}
        response = self._api_client.post("/verification", fields)
        if APIClient.can_proceed(response):
            response_body = response.json()
            if response_body["verified"]:
                self._subscription = Subscription(
                    self._api_client,
                    response_body["idSubscription"],
                    response_body["idActor"],
                    response_body["db"])
                return True
        return False
