class Project(object):
    def __init__(self, name, path, jira_url, username, password, hours_per_day=6):
        assert (isinstance(name, str))
        assert (isinstance(path, str))
        self.password = password
        self.username = username
        self.jira_url = jira_url
        self.name = name
        self.path = path
        self.hours_per_day = hours_per_day

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_jira_url(self):
        return self.jira_url

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_log_path(self):
        return self.path + '/.git/logs/checkout_history'

    def get_hours_per_day(self):
        return self.hours_per_day
