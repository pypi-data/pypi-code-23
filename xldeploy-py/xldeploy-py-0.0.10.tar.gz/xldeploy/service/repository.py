from xldeploy.domain.ConfigurationItem import ConfigurationItem

class RepositoryService:

    __path = "/repository"

    def __init__(self, http_client):
        self.http_client = http_client

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def create_ci(self, ci):
        input = ci.to_dict()
        data = self.http_client.post(path=self.get_path("ci", ci.id), body=input)
        return ConfigurationItem.as_ci(data)

    def create_list(self, cis):
        input = []
        for ci in cis:
            input.append(ci.to_dict())

        data = self.http_client.post(path=self.get_path("cis"), body=input)
        return ConfigurationItem.as_cis(data)

    def copy(self, id, newId):
        data = self.http_client.post(path=self.get_path("copy", id), params={"newId" : newId})
        return ConfigurationItem.as_ci(data)

    def delete(self, id):
        self.http_client.delete(path=self.get_path("ci", id))

    def delete_list(self, ids):
        self.http_client.post(path=self.get_path("cis", "delete"), body=ids)

    def exists(self, id):
        data = self.http_client.get(path=self.get_path("exists", id))
        return data["boolean"]

    def move(self, id, newId):
        data = self.http_client.post(path=self.get_path("move", id), params={"newId" : newId})
        return ConfigurationItem.as_ci(data)

    def read(self, id):
        data = self.http_client.get(path=self.get_path("ci", id))
        return ConfigurationItem.as_ci(data)

    def read_list(self, ids):
        data = self.http_client.get(path=self.get_path("ci", "read"), body=ids)
        return ConfigurationItem.as_cis(data)

    def rename(self, id, newName):
        data = self.http_client.post(path=self.get_path("rename", id), params={"newName" : newName})
        return ConfigurationItem.as_ci(data)

    def update_artifact(self, artifact):
        return artifact

    def update_ci(self, ci):
        input = ci.to_dict()
        data = self.http_client.put(path=self.get_path("ci", id), body=input)
        return ConfigurationItem.as_ci(data)

    def update_list(self, cis):
        input = []
        for ci in cis:
            input.append(ci.to_dict)
        data = self.http_client.put(path=self.get_path("cis"), body=input)
        return ConfigurationItem.as_cis(data)

    # query_params needs to be build using QueryBuilder
    def query(self, query_params):
        return self.http_client.get(path=self.get_path("query"), params=query_params)

    # repository.create(ArtifactAndData artifact) : ConfigurationItem
    def create_artifact(self, artifact):
        raise Exception('Not implemented.')

    # repository.search(String ciType, Calendar before) : List
    def search(self, ciType, before):
        raise Exception('Not implemented.')

    # repository.search(String ciType) : List
    def search(self, type):
        raise Exception('Not implemented.')

    # repository.search(String ciType, String parent) : List
    def search(self, ciType, parent):
        raise Exception('Not implemented.')

    # repository.searchByName(String name) : List
    def search_by_name(self, name):
        raise Exception('Not implemented.')

    # repository.exportArchivedTasks(String filePath, String beginDate, String endDate) : void
    def export_archived_tasks(self, filePath, beginDate, endDate):
        raise Exception('Not implemented.')

    # repository.exportArchivedTasks(String filePath) : void
    def export_archived_tasks(self, filePath):
        raise Exception('Not implemented.')

    # repository.exportCis(String exportRootId) : String
    def export_cis(self, exportRootId):
        raise Exception('Not implemented.')

    # repository.exportCis(String exportRootId, String exportDir) : String
    def export_cis(self, exportRootId, exportDir):
        raise Exception('Not implemented.')

    # repository.exportCisAndWait(String exportRootId, String exportDir) : String
    def export_cis_and_wait(self, export_rootId, exportDir):
        raise Exception('Not implemented.')

    # repository.exportCisAndWait(String exportRootId) : String
    def export_cis_and_wait(self, exportRootId):
        raise Exception('Not implemented.')

    # repository.exportDar(String directoryPath, String versionId) : void
    def export_dar(self, directoryPath, versionId):
        raise Exception('Not implemented.')

    # repository.getArchivedTaskList() : List
    def get_archived_task_list(self):
        raise Exception('Not implemented.')

    # repository.getArchivedTasksList(String beginDate, String endDate) : List
    def get_archived_tasks_list(self, begin_date, end_date):
        raise Exception('Not implemented.')

    # repository.importCis(String archiveLocation) : String
    def import_cis(self, archiveLocation):
        raise Exception('Not implemented.')

    # repository.importCisAndWait(String archiveLocation) : void
    def import_cis_and_wait(self, archiveLocation):
        raise Exception('Not implemented.')