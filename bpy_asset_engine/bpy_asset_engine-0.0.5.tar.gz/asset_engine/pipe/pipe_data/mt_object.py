class User(object):
    def __init__(self):
        self.username = None
        self.id = None
        self.token = None
        self.projects = []
        self.active_project = None


class Project(object):
    def __init__(self):
        self.name = None
        self.xml_path = None
        self.project_dict = None
        self.project_data = []
        self.assets = None
        self.tasks = []
        self.sequences = None
        self.shots = None
        self.active_task = None

        self.task_url = None
        self.asset_url = None
        self.shot_url = None
        self.root_url = None
        self.file_url = None

    def create_project_urls(self):
        self.task_url = 'https://maketheory.com/api/task/' + self.name + '/tasks/users/'
        self.asset_url = 'https://maketheory.com/api/task/' + self.name + '/assets'
        self.shot_url = 'https://maketheory.com/api/task/' + self.name + '/shots'
        self.root_url = 'https://maketheory.com/api/sync/folders/' + self.name + '/root'
        self.file_url = 'https://maketheory.com/api/sync/files/?project=' + self.name


class Asset(object):
    def __init__(self):
        self.name = None
        self.xml_path = None
        self.asset_dict = None
        self.asset_data = None


class Sequence(object):
    def __init__(self):
        self.name = None
        self.xml_path = None
        self.sequence_dict = None
        self.sequence_data = None


class Shot(object):
    def __init__(self):
        self.name = None
        self.xml_path = None
        self.shot_dict = None
        self.shot_data = None


class Task(object):
    def __init__(self):
        self.name = None
        self.task_dna = None
        self.task_dict = None
        self.task_data = None
        self.asset = None
        self.path = None