
class Summary(object):

    def __init__(self, client, check, resolution, start, end):
        self.client = client
        self.check = check
        self.resolution = resolution
        self.start = start
        self.end = end

    def retrieve(self):
        response = self.client.api.send("get", "summary.performance", self.check._id, params={
            "from": self.start.timestamp(),
            "to": self.end.timestamp(),
            "resolution": self.resolution,
            "includeuptime": True
        })
        self.series = response['summary'][self.resolution + "s"]
