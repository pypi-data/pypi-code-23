"""Testing utils."""
import json

from django.test.client import Client


class JSONClient(Client):
    """Django client extended to handle json.

    Sets headers for JSON handling and serializes python data into JSON.

    Attributes
    ----------
    JSON_MIME : str
        JSON Mime type.
    """
    JSON_MIME = "application/json"

    def _json_call(self, path, data=None, method="post", **kwargs):
        """Automatically serializes python to JSON and the appropriate headers.

        Parameters
        ---------
        path : str
        data : dict, list
        method : str
            Https method to use.

        Returns
        -------
        Response
            The same response type the original client returns.

        """
        fn = getattr(super(), method.lower())
        payload = json.dumps(data) if data else None
        return fn(path, payload, content_type=self.JSON_MIME, HTTP_ACCEPT=self.JSON_MIME, **kwargs)

    def get(self, *args, **kwargs):
        """Request a response from the server using GET.

        Refer to ``django.test.client.Client.get`` for accepted params.
        """
        return self._json_call(*args, method="get", **kwargs)

    def post(self, *args, **kwargs):
        """Request a response from the server using POST.

        Refer to ``django.test.client.Client.post`` for accepted params.
        """
        return self._json_call(*args, method="post", **kwargs)

    def put(self, *args, **kwargs):
        """Request a response from the server using PUT.

        Refer to ``django.test.client.Client.put`` for accepted params.
        """
        return self._json_call(*args, method="put", **kwargs)

    def patch(self, *args, **kwargs):
        """Request a response from the server using PATCH.

        Refer to ``django.test.client.Client.patch`` for accepted params.
        """
        return self._json_call(*args, method="patch", **kwargs)

    def delete(self, *args, **kwargs):
        """Request a response from the server using DELETE.

        Refer to ``django.test.client.Client.delete`` for accepted params.
        """
        return self._json_call(*args, method="delete", **kwargs)
