from directory_client_core.authentication import SessionSSOAuthenticator
from directory_client_core.base import BaseAPIClient


class ExportReadinessAPIClient(BaseAPIClient):

    endpoints = {
        'triage-result': 'export-readiness/triage/',
        'create-retrieve-article-read': 'export-readiness/article-read/',
        'create-retrieve-task-completed': 'export-readiness/task-completed/'
    }
    authenticator = SessionSSOAuthenticator

    def retrieve_triage_result(self, sso_session_id):
        return self.get(
            self.endpoints['triage-result'],
            authenticator=self.authenticator(sso_session_id),
        )

    def create_triage_result(self, form_data, sso_session_id):
        return self.post(
            self.endpoints['triage-result'],
            data=form_data,
            authenticator=self.authenticator(sso_session_id),
        )

    def update_triage_result(self, form_data, sso_session_id):
        return self.patch(
            self.endpoints['triage-result'],
            data=form_data,
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_article_read(self, sso_session_id):
        return self.get(
            self.endpoints['create-retrieve-article-read'],
            authenticator=self.authenticator(sso_session_id),
        )

    def create_article_read(self, article_uuid, sso_session_id):
        return self.post(
            self.endpoints['create-retrieve-article-read'],
            data={'article_uuid': article_uuid},
            authenticator=self.authenticator(sso_session_id),
        )

    def bulk_create_article_read(self, article_uuids, sso_session_id):
        return self.post(
            self.endpoints['create-retrieve-article-read'],
            data=[{'article_uuid': uuid} for uuid in article_uuids],
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_task_completed(self, sso_session_id):
        return self.get(
            self.endpoints['create-retrieve-task-completed'],
            authenticator=self.authenticator(sso_session_id),
        )

    def create_task_completed(self, task_uuid, sso_session_id):
        return self.post(
            self.endpoints['create-retrieve-task-completed'],
            data={'task_uuid': task_uuid},
            authenticator=self.authenticator(sso_session_id),
        )
