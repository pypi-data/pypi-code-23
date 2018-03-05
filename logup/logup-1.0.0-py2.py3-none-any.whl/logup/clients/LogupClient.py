from co.logup.clients.APIClient import APIClient
from co.logup.endpoints.Subscription import Subscription
from co.logup.endpoints.Verification import Verification


class LogupClient:

    def __init__(self, id_gate, gate_secret_key, version="v1_1"):
        """
        Create an instance of Logup Client using the default API Version

        :type id_gate: str
        :param id_gate: Your gate id

        :type gate_secret_key: str
        :param gate_secret_key: Your gate secret
        """
        # APIClient.verify_api_version(version)
        self._id_gate = id_gate
        self._gate_secret_key = gate_secret_key
        self._api_client = APIClient(self._id_gate, self._gate_secret_key, version)
        self._subscription = None
        self._verification = Verification(self._api_client)

    @property
    def subscription(self):
        # type: () -> Subscription
        """
        Get subscription loaded

        :rtype: Subscription
        :return Subscription loaded
        """
        return self._subscription

    def subscription_custom(self, id_subscription):
        # type: (str) -> Subscription
        """
        Get custom subscription

        :type id_subscription: str
        :param id_subscription: Id subscription you want to load

        :rtype: Subscription
        :return: Instance of subscription class created
        """
        return Subscription(self._api_client, id_subscription)

    def is_logup_verified(self, logup_token, is_new_user):
        # type: (str, bool) -> bool
        """
        Check if the logup token received is verified or not.

        :type logup_token: str
        :param logup_token: Logup token received.

        :type is_new_user: bool
        :param is_new_user: True if it's a new user for your website, false otherwise

        :rtype: bool
        :return: True if the logup token has been verified, false otherwise
        """
        if self._verification.verify_user(logup_token):
            self._subscription = self._verification.subscription
            self._subscription.is_new_user = is_new_user
            return True
        return False
