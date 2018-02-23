import base64

class AlgmResponse(object):
    def __init__(self, result, metadata):
        self.result = result
        self.metadata = metadata

    def __repr__(self):
        return 'AlgmResponse(result=%s,metadata=%s)' % (self.result, self.metadata)

    @staticmethod
    def create_algo_response(responseJson):
        # Parse response JSON
        if 'error' in responseJson:
            # Failure
            raise AlgmException(responseJson['error'])
        else:
            metadata = Metadata(responseJson)
            # Success, check content_type
            # if responseJson['metadata']['content_type'] == 'binary':
            #     # Decode Base64 encoded binary file
            #     return AlgmResponse(base64.b64decode(responseJson['result']), metadata)
            # elif responseJson['metadata']['content_type'] == 'void':
            #     return AlgmResponse(None, metadata)
            # else:
            return AlgmResponse(responseJson['data'], metadata)


class AlgmException(Exception):
    def __init__(self, error):
        self.message = error['message']
        self.stacktrace = None
        if 'stacktrace' in error:
            self.stacktrace = error['stacktrace']

    def __str__(self):
        return self.message

class Metadata(object):
    def __init__(self, metadata):
        self.duration = metadata['duration']
        self.stdout = None
        if 'stdout' in metadata:
            self.stdout = metadata['stdout']
        self.full_metadata = metadata

    def __repr__(self):
        return "Metadata(duration=%s,stdout=%s)" % ( self.duration, self.stdout)
