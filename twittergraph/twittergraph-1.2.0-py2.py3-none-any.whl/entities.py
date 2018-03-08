class Follower(object):
    md = {}
    idMe = None
    nameMe = None
    idFollower = None
    nameFollower = None
    def __init__(self, idMe, nameMe, idFollower, nameFollower):
        self.idMe = self.md["idMe"] = idMe
        self.nameMe = self.md["nameMe"] = nameMe
        self.idFollower = self.md["idFollower"] = idFollower
        self.nameFollower = self.md["nameFollower"] = nameFollower
        
    def __getitem__(self,key):
        return self.md[key]
    def __setitem__(self, key, item):
        self.md[key] = item
    def dicti(self):
        return self.md
class Following(object):
    md = {}
    idMe = None
    nameMe = None
    idFollowing = None
    nameFollowing = None
    def __init__(self, idMe, nameMe, idFollowing, nameFollowing):
        self.idMe = self.md["idMe"] = idMe
        self.nameMe = self.md["nameMe"] = nameMe
        self.idFollowing = self.md["idFollowing"] = idFollowing
        self.nameFollowing = self.md["nameFollowing"] = nameFollowing
    def __str__(self):
        return self.idMe+","+self.nameMe+","+self.idFollowing+","+self.nameFollowing
    def __getitem__(self,key):
        return self.md[key]
    def __setitem__(self, key, item):
        self.md[key] = item
    def dicti(self):
        return self.md
