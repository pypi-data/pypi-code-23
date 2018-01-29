import sanitize

class AthleteList(list):
    def __init__(self,a_name,a_dob=None,a_times=[]):
        list.__init__([])
        self.name = a_name
        self.dob = a_dob
        self.times = a_times
        print("创建实例")
    def top3(self):
        return sorted(set([sanitize(t) for t in self.times]))[0:3]
