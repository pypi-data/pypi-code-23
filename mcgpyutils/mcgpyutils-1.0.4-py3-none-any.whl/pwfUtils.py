from datetime import date

import requests

class ProWorkflowUtils:
    CLIENT_JOB_NUMBER_ID = 2
    INCLUDE_IN_TIMESHEETS_ID = 3
    RECONCILIATION_HOURS_ID = 4

    '''
    @param user: the username to login to ProWorkflow
    @param password: the password to login to ProWorkflow
    @param api_key: the ProWorkflow API key
    @param base_url: the ProWorkflow API base URL
    '''
    def __init__(self, user, password, api_key, base_url):
        self.user = user
        self.password = password
        self.api_key = api_key
        self.base_url = base_url


    '''
    Gets all project data (open and closed) that exists for the current user.

    @param desc: specifies if the data should be returned in descending order
                 (oldest to newest)
    @param params: an optional list of tuples of additional parameters
    @return: project data in JSON format
    '''
    def get_projects(self, desc=False, params=None):
        headers = {"apikey": self.api_key}

        extra_params = ""
        if params:
            extra_params += self._build_extra_params_string(params)
        if desc:
            extra_params += "&sortorder=desc&sortby=startdate"

        r = requests.get("{0}/projects?status=all{1}".format(self.base_url, extra_params), auth=(self.user, self.password), headers=headers)
        return r.json()


    '''
    Gets the data for the specified project ID.

    @param project_id: the project to query
    @return: data for the specified project in JSON format
    '''
    def get_project(self, project_id):
        headers = {"apikey": self.api_key}
        r = requests.get("{0}/projects/{1}".format(self.base_url, project_id), auth=(self.user, self.password), headers=headers)
        return r.json()


    '''
    Returns an alphabetically sorted list of unique client names.

    @return: an alphabetically sorted list of unique client names
    '''
    def get_client_names(self):
        client_names = []

        headers = {"apikey": self.api_key}
        r = requests.get("{0}/companies".format(self.base_url), auth=(self.user, self.password), headers=headers)

        companies = r.json()
        for company in companies["companies"]:
            if company["type"] == "client" and company["name"] not in client_names:
                client_names.append(company["name"])

        return client_names


    '''
    Builds a list of client projects based on the given @client.

    @param projects: JSON data containing all current ProWorkflow projects
    @param client: the client used to filter the @projects JSON data
    @return: a list of JSON filtered by @client
    '''
    def get_projects_by_client_name(self, projects, client):
        client_projects = []

        all_projects = projects["projects"]
        for project in all_projects:
            if (project["companyname"]).lower() == client:
                client_projects.append(project)

        return client_projects


    '''
    Gets project data for the given @project_id.

    @param project_id: the project to query
    @return: project data in JSON format
    '''
    def get_project_by_id(self, project_id):
        headers = {"apikey": self.api_key}
        r = requests.get("{0}/projects/{1}".format(self.base_url, project_id), auth=(self.user, self.password), headers=headers)
        return r.json()


    '''
    Updates fields for a given @project_id with the data in @payload.

    @param project_id: the project ID to update
    @param payload: a dict of values used to update the associated project
    @return: results of project field PUT in JSON format
    '''
    def put_project_field(self, project_id, payload):
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        r = requests.put("{0}/projects/{1}".format(self.base_url, project_id), data=payload, auth=(self.user, self.password), headers=headers)
        return r.json()


    '''
    Gets the aggregate time of the given @project_id within a range.

    @param project_id: the project to query
    @param timefrom: a string in the format YYYY-MM-DD specifying the beginning
                     of the query range
    @param timefrom: a string in the format YYYY-MM-DD specifying the end of the
                     query range
    @param params: an optional list of tuples of additional parameters
    @return: project time data in JSON format
    '''
    def get_project_time(self, project_id, timefrom, timeto, params=None):
        headers = {"apikey": self.api_key}

        extra_params = self._build_extra_params_string(params)

        r = requests.get("{0}/projects/{1}/time?trackedfrom={2}&trackedto={3}{4}".format(self.base_url, project_id, timefrom, timeto, extra_params), auth=(self.user, self.password), headers=headers)
        return r.json()


    '''
    Builds a query string from a given list of tuples.

    @param params: a list of tuples of additional parameters
    @return: the query string
    '''
    def _build_extra_params_string(self, params):
        extra_params = ""
        if params:
            for key, value in params:
                extra_params += "&{0}={1}".format(key, value)
        return extra_params
